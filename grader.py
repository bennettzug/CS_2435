import os
import sys
import io
import shutil
import tempfile
import pathlib
import glob
import time
import re
import asyncio
import difflib
import traceback

import zipfile
import importlib
import configparser
import contextlib
import multiprocessing

RUN_INSTRUCTIONS = """

HOW TO RUN THIS SCRIPT WITHIN SPYDER:

    1. Press Ctrl+F6 (while you are reading this in Spyder)
        to open the Run Configuration menu
    2. Select the option "Run file with custom configuration"
    3. In the Console pane:
        a. Select the option "Execute in an external system terminal"
        b. Check the box "Interact with the Python console after execution"
    4. The grader script can now run in Spyder

    You can close the window with the script output when it is done.
"""


GRADER_VERSION = 5
PYTHON_VERSION_MAJOR = 3
PYTHON_VERSION_MINOR = 9
ERROR_LOG = "error.log"

IGNORED_STYLE_ERRORS = ["W", "E115", "E116", "E117", "E12", "E26", "E3"]

TESTZIP_RE = re.compile("^tests-((lab([0-9]*))\.zip)$")
NOOP = lambda *args, **kwargs: None

if "debugpy" in sys.modules:
    print("[!!!!!] Debugging tools detected. [!!!!!]")
    print("Running the grader with debugging hooks causes problems.")
    print(
        "If you are using VSCode or another IDE, ensure you are not enabling debugging."
    )


def write_error(msg, out=sys.stdout):
    out.write(msg + "\n")
    out.flush()


class GraderException(Exception):
    pass


class GraderTestResult:
    HEADER_TAG = chr(0x06) * 2
    ERROR_ID = "error"

    def __init__(self, id, passed=True, runtime=None):
        self.report = None
        self.id = id
        self.index = -1

        self.score = 1.0 if passed else 0.0
        self.info = None
        self.runtime = runtime
        self.output = []

    def get_name(self):
        src = self.report.source if self.report else "<unknown>"
        return "{src:s}/{id:s}".format(src=src, id=self.id)

    def __str__(self):
        return "<TestResult: {name:s} score={score:.2f}>".format(
            name=self.get_name(),
            score=self.score,
        )

    def attach_output(self, label, data=None, prefix="  "):
        self.output.append(
            "{htag:s}<{tag:s}>".format(htag=GraderTestResult.HEADER_TAG, tag=label)
        )
        if data is None:
            return

        if isinstance(data, str):
            data = data.splitlines()
        self.output += [prefix + x.rstrip("\r\n") for x in data]
        self.output.append(prefix)

    def add_diff(self, label, actual, expect):
        self.attach_output(label)
        self.output += list(
            difflib.Differ(charjunk=lambda _: False).compare(
                expect.splitlines(), actual.splitlines()
            )
        )
        self.output.append("  ")

    def get_output(self):
        yield from self.output

    def set_score(self, score=0.0, info=None):
        self.score = score
        self.info = info

    def is_passing(self):
        return self.score == 1.0 and self.runtime <= self.report.timeout


class GraderReport:
    def __init__(self, source, tests=0, error=None):
        self.source = source
        self.style_errors = []

        self.timeout = 1
        self.soft_timeout = 1

        self.tests = tests
        self.results = list()
        self.errors = set()
        if error is not None:
            self.errors.add(error)
            self.tests = None

    def make_result(self, test_id):
        result = GraderTestResult(id=test_id, passed=True)
        result.report = self
        return result

    def add_result(self, result):
        result.index = len(self.results)
        self.results.append(result)

    def make_error(self):
        result = self.make_result(GraderTestResult.ERROR_ID)
        result.set_score(score=0.0)
        return result

    def count_passed(self):
        return sum(1 if x.is_passing() else 0 for x in self.results)

    def count_timeouts(self):
        return sum(1 if x.runtime >= self.timeout else 0 for x in self.results)

    def count_soft_timeouts(self):
        return sum(1 if x.runtime >= self.soft_timeout else 0 for x in self.results)

    def has_errors(self):
        return self.errors or self.style_errors

    def get_grade(self, scale=1.0):
        if not self.tests:
            return 0.0
        return scale * sum(x.score for x in self.results) / self.tests

    def is_passing(self):
        return self.get_grade() == 1.0 and not self.errors

    def is_complete(self):
        return self.tests is None or len(self.results) == self.tests


@contextlib.contextmanager
def cwd(path):
    owd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(owd)


def load_pycodestyle(pycodestyle_src):
    try:
        spec = importlib.util.spec_from_loader(
            "pycodestyle", loader=None, origin="pycodestyle.py"
        )
        pycodestyle = importlib.util.module_from_spec(spec)
        pycodestyle.__file__ = __file__
        exec(pycodestyle_src.read_text(), pycodestyle.__dict__)

        class StoredReport(pycodestyle.BaseReport):
            """Collect and results of the checks."""

            def __init__(self, options):
                super().__init__(options)
                self._fmt = "{path:s}:{row:d}:{col:d}: [{code:s}] {text:s}"
                self._filename = "???"

            def init_file(self, filename, lines, expected, line_offset):
                """Signal a new file."""
                self._message_log = []
                return super().init_file(filename, lines, expected, line_offset)

            def error(self, line_number, offset, text, check):
                """Report an error, according to options."""
                code = super().error(line_number, offset, text, check)
                if code is not None:
                    self._message_log.append(
                        (line_number, offset, code, text[5:], check.__doc__)
                    )
                return code

            def get_messages(self):
                self._message_log.sort()
                messages = []
                for line_number, offset, code, text, doc in self._message_log:
                    messages.append(
                        self._fmt.format(
                            path=os.path.basename(self.filename),
                            row=self.line_offset + line_number,
                            col=offset + 1,
                            code=code,
                            text=text,
                        )
                    )
                return messages

        # setup code checker with the correct style warnings
        return pycodestyle.StyleGuide(
            max_line_length=120, reporter=StoredReport, ignore=IGNORED_STYLE_ERRORS
        )
    except:
        traceback.print_exc()
        pass
    return None


def run_interactive(cmd, stdin, source=None, tlimit=1_000_000):
    if source is None:
        source = cmd[1]  # TODO: remove this hack

    async def get_line(output, pipe):
        line = await pipe.read(1024 * 16)
        output.append(
            line.decode(encoding=sys.stdout.encoding, errors="backslashreplace")
        )

    async def __run():
        tt = time.monotonic()
        proc = await asyncio.subprocess.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        output = []
        exitcode, err = None, ""
        try:
            for line in (x for x in stdin.splitlines(keepends=True) if x):
                await asyncio.wait_for(get_line(output, proc.stdout), tlimit)
                if time.monotonic() - tt > tlimit:
                    raise asyncio.TimeoutError("aggregate process time expired")
                output.append(line)
                proc.stdin.write(line.encode("utf-8"))
            await asyncio.wait_for(get_line(output, proc.stdout), tlimit)
            await asyncio.wait_for(proc.wait(), tlimit)

            exitcode = proc.returncode
            err = await proc.stderr.read()
            err = err.decode(encoding=sys.stderr.encoding, errors="backslashreplace")

        except asyncio.TimeoutError:
            proc.kill()
            if proc._transport:  # this is a HACK
                proc._transport.close()
            await proc.wait()

        runtime = time.monotonic() - tt
        if runtime >= tlimit:
            err = "[{source:s}] maximum runtime allowance ({limit:.2f} seconds) exceeded".format(
                source=source, limit=tlimit
            )
            exitcode = None

        output_text = re.sub(r"[\r\n]+", r"\n", "".join(output))
        return exitcode, output_text, err, runtime

    return asyncio.run(__run())


def error_cleanup(msg):
    def repfn(m):
        return 'File "{base:s}", line {line:s}'.format(
            base=os.path.basename(m.group(1)), line=m.group(2)
        )

    TRACEBACK_HEADER = re.compile('File "(.+)", line (\d+)')
    return re.sub(TRACEBACK_HEADER, repfn, msg)


def print_progress(label, x, n, failed=0, SIZE=30):
    if n == 0:
        return  # raise GraderException("No tests found for grader.")
    fill = SIZE * x // n
    bar = chr(9608) * fill + chr(9617) * (SIZE - fill)
    desc = "(Test {num:03d}/{cnt:03d})".format(num=x, cnt=n)
    if failed > 0:
        desc += " ({:d} tests failed)".format(failed)
    print(
        "\r{bar:s} [{perc:03d}%] {desc:s} - {label:s}".format(
            bar=bar, perc=100 * x // n, desc=desc, label=label
        ),
        end="",
    )
    if x == n:
        print("")
    sys.stdout.flush()


def print_report_progress(report, x):
    print_progress(report.source, x, report.tests, failed=x - report.count_passed())


def test_one(folder, srcpath=None, config=None, style=None, quiet=False):
    console_error = NOOP if quiet else write_error
    console_msg = NOOP if quiet else print

    if not config:
        config_file = folder / "config.ini"
        config = configparser.ConfigParser()
        if config_file.exists():
            config.read_string(config_file.read_text(), source=str(config_file))

    source = config.get("grader-config", "source")
    srcpath = srcpath or source

    def illegal_imports(srcpath, allowed_modules):
        # TODO: all of this
        return set()

    if not os.path.exists(srcpath):
        message = ["Source file {src:s} is missing. Tests omitted.".format(src=source)]
        m = difflib.get_close_matches(source, glob.iglob("*.py"), n=1, cutoff=0.8)
        if len(m) > 0:
            message.append(
                "This name looks close, perhaps a typo? {matches[0]:s}".format(
                    matches=m
                )
            )
        console_error("\n".join(message))
        yield GraderReport(
            source, error="".join(x + "\n" for x in message)
        ).make_error()
        return

    def make_text_stream(x, config):
        # for really specific file encoding issues
        encoding_flags = dict()
        enc = config.get("grader-config", "encoding", fallback=None)
        if enc:
            encoding_flags["encoding"] = enc
            encoding_flags["errors"] = "ignore"
        return (
            x
            if isinstance(x, io.TextIOWrapper)
            else io.TextIOWrapper(x, **encoding_flags)
        )

    # return (match, feedback)
    # if feedback is None, diff of outputs will be used for feedback
    def output_matches(a, b, type):
        CHUNK_SIZE = 2**10
        ax, bx = 1, 1
        while ax and bx:
            ax, bx = a.read(CHUNK_SIZE), b.read(CHUNK_SIZE)
            if ax != bx:
                return False, None
        return True, None

    # a custom grader for evaluating output
    gmodule = None
    custom_grader = folder / "custom-grader.py"
    if custom_grader.exists():
        try:
            spec = importlib.util.spec_from_loader("grader", loader=None)
            gmodule = importlib.util.module_from_spec(spec)
            exec(custom_grader.read_text(), gmodule.__dict__)
        except:
            raise GraderException(
                "Could not open custom grader for {src:s}".format(src=source)
            )

    check_output = output_matches
    if gmodule and hasattr(gmodule, "check_output"):
        check_output = gmodule.check_output

    # check module imports
    allowed_modules = [
        x.strip()
        for x in config.get("grader-config", "allowed-modules", fallback="").split(",")
        if x
    ]
    illegal_found = illegal_imports(srcpath, allowed_modules)
    if illegal_found:
        for module_name in illegal_found:
            console_error("Illegal module import: {:s}".format(module_name))
        yield GraderReport(
            source, error="Illegal imports: {:s}\n".format(",".join(illegal_found))
        ).make_error()
        return

    # check if the source code passes any tests
    if gmodule and hasattr(gmodule, "check_source"):
        src_error = gmodule.check_source(srcpath)
        if src_error:
            for msg in src_error:
                console_error(msg)
            yield GraderReport(
                source, error="".join(x + "\n" for x in src_error)
            ).make_error()
            return

    report = GraderReport(source=source)
    report.style_errors = style if style else []

    report.timeout = config.getint("grader-config", "timeout", fallback=1)
    report.soft_timeout = config.getint(
        "grader-config", "soft-timeout", fallback=report.timeout
    )

    if gmodule and hasattr(gmodule, "grade"):
        yield from gmodule.grade(sys.modules[__name__], report, errors=report.errors)
    else:
        stdin_files = [x for x in folder.iterdir() if x.name.endswith(".stdin")]
        numtests = len(stdin_files)

        report.tests = numtests
        for testnum, stdin_file in enumerate(stdin_files):
            test_id = stdin_file.name.split(".")[0]

            # custom config file per-test supported
            test_config_file = folder / "{id:s}-config.ini".format(id=test_id)
            test_config = configparser.ConfigParser()
            test_config.read_dict(config)
            if test_config_file.exists():
                test_config.read_string(
                    test_config_file.read_text(), source=str(test_config_file)
                )

            test_name = test_config.get(
                "test-config", "test-name", fallback="#" + test_id
            )

            # this will get marked as failed if we find a mismatch
            test_result = report.make_result(test_name)

            with tempfile.TemporaryDirectory() as workspace:
                stdin_text = ""  # text to be input to the process via stdin
                try:
                    if stdin_file.exists():
                        stdin_text = stdin_file.read_text()
                except:
                    raise GraderException(
                        "\n".join(
                            [
                                "Failed to setup input data for testing ({src:s}, test {test:s})".format(
                                    src=source, test=test_name
                                ),
                                "Issue with getting standard input (keyboard input) for test case:",
                                traceback.format_exc(),
                            ]
                        )
                    )

                input_file_tag = "{id:s}-inp-".format(id=test_id)
                output_file_tag = "{id:s}-out-".format(id=test_id)
                input_raw_set = set()
                output_file_set = set()

                for file in folder.iterdir():
                    if file.name.startswith(input_file_tag):
                        input_raw_set.add(file.name)
                        input_file_name = file.name[len(input_file_tag) :]
                        try:
                            with open(
                                os.path.join(workspace, input_file_name), "w"
                            ) as inpc:
                                with file.open("r") as inpfd:
                                    shutil.copyfileobj(
                                        make_text_stream(inpfd, test_config), inpc
                                    )
                        except:
                            raise GraderException(
                                "\n".join(
                                    [
                                        "Failed to setup input data for testing ({src:s}, test {test:s})".format(
                                            src=source, test=test_name
                                        ),
                                        'Issue with getting input file "{fn:s}" for test case:'.format(
                                            fn=input_file_name
                                        ),
                                        traceback.format_exc(),
                                    ]
                                )
                            )
                    elif file.name.startswith(output_file_tag):
                        output_file_set.add(file.name[len(output_file_tag) :])

                try:
                    with open(os.path.join(workspace, source), "w") as wsrc:
                        # open a local file version
                        with open(srcpath, "r") as source_file:
                            shutil.copyfileobj(source_file, wsrc)

                    with cwd(workspace):
                        (
                            exit_code,
                            output_text,
                            stderr,
                            test_result.runtime,
                        ) = run_interactive(
                            [sys.executable, source],
                            source=source,
                            stdin=stdin_text,
                            tlimit=report.timeout,
                        )

                        stdout_file = folder / "{id:s}.stdout".format(id=test_id)
                        if stdout_file.exists():
                            actual_output = io.StringIO(output_text)
                            with stdout_file.open("r") as expected_stream:
                                expect_output = make_text_stream(
                                    expected_stream, test_config
                                )
                                result, feedback = check_output(
                                    actual_output, expect_output, type="stdout"
                                )
                                if not result:
                                    test_result.set_score(
                                        score=0.0, info="console output mismatch"
                                    )

                                label = "console output"
                                if feedback is not None:
                                    test_result.attach_output(label, feedback)
                                else:
                                    expect_output.seek(0)
                                    test_result.add_diff(
                                        label, output_text, expect_output.read()
                                    )

                        for in_filename in input_raw_set:
                            input_file_name = in_filename[len(input_file_tag) :]
                            if os.path.getsize(input_file_name) < 10 * 1024:
                                with open(input_file_name, "r") as inp_file:
                                    test_result.attach_output(
                                        "input file: {file:s}".format(
                                            file=input_file_name
                                        ),
                                        inp_file.readlines(),
                                    )

                        for out_filename in output_file_set:
                            if os.path.exists(out_filename):
                                with open(out_filename, "r") as actual_output:
                                    zip_file = folder / "{id:s}-out-{base:s}".format(
                                        id=test_id, base=out_filename
                                    )
                                    with zip_file.open("r") as expected_stream:
                                        expect_output = make_text_stream(
                                            expected_stream, test_config
                                        )
                                        result, feedback = check_output(
                                            actual_output,
                                            expect_output,
                                            type="file:" + out_filename,
                                        )
                                        if not result:
                                            test_result.set_score(
                                                score=0.0,
                                                info="output file contents incorrect: {file:s}".format(
                                                    file=out_filename
                                                ),
                                            )

                                        label = "output file: {file:s}".format(
                                            file=out_filename
                                        )
                                        if feedback is not None:
                                            test_result.attach_output(label, feedback)
                                        else:
                                            for x in (actual_output, expect_output):
                                                x.seek(0)
                                            test_result.add_diff(
                                                label,
                                                actual_output.read(),
                                                expect_output.read(),
                                            )
                            else:
                                test_result.set_score(
                                    score=0.0,
                                    info="file expected, but missing: {file:s}".format(
                                        file=out_filename
                                    ),
                                )
                                test_result.attach_output(
                                    "output file missing: {file:s}".format(
                                        file=out_filename
                                    ),
                                    "",
                                )

                        if exit_code != 0 or len(stderr) > 0:
                            clean_stderr = error_cleanup(stderr)
                            test_result.attach_output(
                                "runtime errors (exit code: {x:s})".format(
                                    x=str(exit_code)
                                ),
                                clean_stderr,
                            )
                            test_result.set_score(
                                score=0.0,
                                info="runtime errors or nonstandard exit code",
                            )
                            report.errors.add(clean_stderr)
                except GraderException as e:
                    raise e
                except Exception:
                    traceback.print_exc()
                    raise GraderException(
                        "An error occurred when running the program ({src:s}) against test data".format(
                            src=source
                        )
                    )

                report.add_result(test_result)
                yield test_result


def _get_report(results):
    reports = {x.report for x in results}
    if len(reports) != 1:
        raise GraderException("Cannot get singular report from mixed results.")
    for report in reports:
        return report


def _get_tests_from_folder(tests_folder):
    tests = list()
    for folder in tests_folder.iterdir():
        if folder.is_dir() and folder.name.startswith("test-"):
            config_file = folder / "config.ini"
            config = configparser.ConfigParser()
            if config_file.exists():
                config.read_string(config_file.read_text(), source=str(config_file))

            package_version = config.getint(
                "grader-config", "grader-version", fallback=0
            )
            if package_version > GRADER_VERSION:
                write_error(
                    "This test zip was compiled for a newer version of the grader."
                )
                write_error(
                    "Please download the newest version of {script:s} from AsULearn before continuing.".format(
                        script=sys.argv[0]
                    )
                )
                return []

            tests.append((folder, config))
    return tests


def test_all(zippath):
    import os.path

    os.chdir(os.path.dirname(os.path.abspath(zippath)))

    def log_error(source):
        from datetime import datetime

        with open(ERROR_LOG, "w") as log:
            log.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")
            log.write("error occurred with {src:s}\n".format(src=source))
            traceback.print_exc(file=log)
        return ERROR_LOG

    this_version = sys.version_info
    if this_version.major < PYTHON_VERSION_MAJOR:
        write_error(
            (
                "Grading is done in Python {maj:d}.{min:d}. You are running Python "
                + "{v.major:d}.{v.minor:d}.\nYou *must* update to Python {maj:d}.{min:d}"
            ).format(maj=PYTHON_VERSION_MAJOR, min=PYTHON_VERSION_MINOR, v=this_version)
        )
    elif this_version.minor != PYTHON_VERSION_MINOR:
        write_error(
            (
                "Grading is done in Python {maj:d}.{min:d}. You are running Python "
                + "{v.major:d}.{v.minor:d}."
            ).format(maj=PYTHON_VERSION_MAJOR, min=PYTHON_VERSION_MINOR, v=this_version)
        )
        write_error(
            "You may encounter minor inconsistencies if you aren't running the correct version."
        )

    if not os.path.exists(zippath):
        write_error("Cannot find test zip.")
        return False
    elif not zipfile.is_zipfile(zippath):
        write_error("Test zip is malformed.")
        write_error(
            "Redownload the test zip and try again. If problems persist, notify your instructor."
        )
        return False

    codechecker = None
    count_tests = 0

    reports = set()
    with zipfile.ZipFile(zippath, "r") as testzip:

        def find_in_zip(name, path):
            for x in path.iterdir():
                if x.name == name:
                    return path
                elif x.is_dir() and x.name != "__MACOSX" and x.name != ".DS_Store":
                    p = find_in_zip(name, x)
                    if p is not None:
                        return p
            return None

        tests_folder = find_in_zip("pycodestyle.py", zipfile.Path(testzip))
        codechecker = load_pycodestyle(tests_folder / "pycodestyle.py")

        test_set = _get_tests_from_folder(tests_folder)
        if not test_set:
            print("No tests found in zip folder {zip:s}?".format(zip=zippath))
            return []

        for folder, config in test_set:
            source = config.get("grader-config", "source")
            try:
                style_errors = []
                if codechecker and os.path.exists(source):
                    style_report = codechecker.check_files([source])
                    style_errors = style_report.get_messages()

                yield from test_one(folder, config=config, style=style_errors)
            except GraderException as e:
                write_error("")
                write_error("<Grader Error> " + str(e))
                write_error(
                    (
                        "If you believe you're seeing this message in error, "
                        + "re-download the grading materials. If problems persist, "
                        + "send {log:s} to your instructor."
                    ).format(log=log_error(source))
                )


def make_submission_zip(testzip, sources):
    base = os.path.basename(testzip)
    output = base.split("-", 1)[-1] if base.startswith("tests-") else "submit.zip"

    print("CORRECTNESS TESTS PASSED FOR ALL COMPLETED PROGRAMS")
    print("Reminder: passing correctness tests does not guarantee full credit.")
    print("Please review the grading rubric on AsULearn for more information.")
    with zipfile.ZipFile(
        output, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as submitzip:
        for source in sources:
            submitzip.write(source)
    print(
        "({output:s} generated in this folder for submission to AsULearn)".format(
            output=output
        )
    )
    return output


def test_via_console(testzip=None):
    passing, reports = True, set()
    with open("feedback.txt", "w") as feedback:
        for result in test_all(testzip):
            print_report_progress(result.report, result.index)
            passing = passing and result.is_passing()
            for line in result.get_output():
                feedback.write(line)
            if result.report.is_complete():
                print_report_progress(result.report, result.report.tests)
                print("")
                reports.add(result.report)

    if passing:
        make_submission_zip(testzip, {x.source for x in reports})
        return True
    else:
        print("The following programs did not pass:")
        for report in reports:
            if not report.is_passing():
                print("-", report.source)
    return False


def test_fallback(testzip=None):
    if testzip is None:
        zips = glob.glob("tests-*.zip")
        if len(zips) == 0:
            print("Could not find test zips.")
            return False
        elif len(zips) == 1:
            testzip = zips[0]
        else:
            for i, zipname in enumerate(zips):
                print("{option:d}) {path:s}".option(i + 1, zipname))
            x = int(input("Select a test zip (type a number): ")) - 1
            testzip = zips[x]

    print("Using", testzip)
    return test_via_console(testzip)


def _run_tests(zippath, q):
    def _send_progress(report, x):
        message = "[{x:d}/{r.tests:d}] Grading {r.source:s}".format(x=x, r=report)
        bar_value = round(100 * x / report.tests)
        q.put(("progress", (message, bar_value)))

    passing, sources = True, set()
    for result in test_all(zippath):
        if result.id != GraderTestResult.ERROR_ID:
            _send_progress(result.report, result.index)
            q.put(("result", result))
        passing = passing and result.is_passing()
        if result.report.is_complete():
            q.put(("report", result.report))
            sources.add(result.report.source)

    output = make_submission_zip(zippath, sources) if passing else None
    last = (
        'Submission zip created: "{output:s}"'.format(output=os.path.abspath(output))
        if output
        else ""
    )
    q.put((None, (last, 100)))


def test_via_gui(testzip=None, autorun=False):
    try:
        import tkinter as tk
        from tkinter import ttk

        from tkinter import filedialog, scrolledtext
    except ImportError as e:
        print("Could not import GUI libraries ({e.name:s})...".format(e=e))
        return test_fallback(testzip)

    TYPE_ZIP = [("Archive (ZIP)", "*.zip")]
    TYPE_PY = [("Python scripts", "*.py")]

    PASS_GIF = b'GIF89a\x10\x00\x10\x00\x84\x00\x00\x04\x82\x04\x8c\xc6\x8cL\xa6L\xd4\xea\xd4$\x92$\xb4\xda\xb4l\xb6l\xec\xf6\xec\x14\x8a\x14\x9c\xce\x9c\\\xae\\\xe4\xf2\xe44\x9a4\xc4\xe2\xc4|\xbe|\xfc\xfe\xfc\x0c\x86\x0c\x94\xca\x94T\xaaT\xdc\xee\xdc,\x96,\xbc\xde\xbct\xbat\xf4\xfa\xf4\x1c\x8e\x1c\xa4\xd2\xa4d\xb2d\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x1b\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05p\xe0&\x8a\x19\x93\x95\xd9\xa8\x1eU\x01\x010\x00e\xd5\xa1:q\x1e[\xaa\xa0\xeb\x02\xd1B\xf2\xfbI\x16\x81"\x00s0\xc4\x02\x03ecC\x84\r\x1a1\x88\x13`\xd8\x14r\x15J,\xb2I\x10\x1e\x07L\x8e\x90\x84!\x06\x9b\xcbF\xa1\x0b\xccc\x18\xf87\x17\xbc\xe33\x08:\x12"\x11jJ\x00\x08d#\x16J<*\x1b\x07K\x86\x18j\x0b\x8f"\x0fq\x12\x12rr#!\x00;'
    FAIL_GIF = b"GIF89a\x10\x00\x10\x00\x84\x00\x00\xe4B\x04\xf4\xb6\xa4\xfc\xde\xd4\xe4f4\xf4\xca\xbc\xe4R\x1c\xf4\xbe\xac\xfc\xfa\xf4\xf4\xd2\xc4\xe4J\x14\xfc\xe6\xdc\xecvL\xe4Z,\xe4F\x0c\xf4\xba\xa4\xe4nD\xf4\xce\xbc\xe4V$\xf4\xc2\xb4\xfc\xd6\xcc\xfc\xea\xe4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x15\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05a`%\x1eKc\x9e\xcb!\xae$\xe0\xben\xca.p\r\xc8\xad]?9P\x04\x8dW \xf2*\xbd\x0c\x15D\x02 I\xbeL\xaf\x82 I\xa8P\x88O\x98T\xa4\xc0fa\xd5\xe4\x12\x16|5)S%Yh\x8dl\t0\x9a\x8b\x81`\xb8\n\x88\xc7\x8b\xa7\xd7\xc1x\x15\x07}~\x80#\x83;*+\x81Fe\x00\x85\x15!\x00;"
    INFO_GIF = b"GIF89a\x10\x00\x10\x00\x84\x00\x00\xfc\xa6\x04\xfc\xd6\x8c\xfc\xee\xcc\xfc\xbeL\xfc\xe6\xb4\xfc\xb2$\xfc\xfa\xec\xfc\xcet\xfc\xf6\xe4\xfc\xea\xc4\xfc\xaa\x14\xfc\xde\xa4\xfc\xf2\xdc\xfc\xb64\xfc\xaa\x0c\xfc\xf2\xd4\xfc\xc6\\\xfc\xea\xbc\xfc\xb6,\xfc\xfe\xfc\xfc\xd2\x84\xfc\xa6\x0c\xfc\xda\x94\xfc\xee\xd4\xfc\xc2T\xfc\xe6\xbc\xfc\xb2,\xfc\xfe\xf4\xfc\xd2|\xfc\xea\xcc\xfc\xe2\xac\xff\xff\xff!\xf9\x04\x01\x00\x00\x1f\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05h\xe0'\x8e_\x97\x90(\xf98\x95\x90\xa2S\x03\x00\xda\xf6\x8e\xd4<\x1f\xf7\xc7\xcc\x05\xcd\xecq\xc3\xccD\n\xc0\xe0\x15\xd1\x19&:\x02L6C\x18t\x9a\t\xc9\xa3\x03\\~\xba\xc5h\"\xd4e.\xdd\x82\xf6\xc3\xed\x1e\x0e]\x80ED\xd5\xbd\xe3\xd9f\\[\x89{\x8cq\x03\x80]\x03Iq\x873\x15\x0c\x04\x0b\x01\x14\x14\x07\x90\x92\x01\x0b\x1e\x0c!\x00;"

    window = tk.Tk()
    window.title("Autograder Tool - {name:s}".format(name=os.path.basename(__file__)))
    window.geometry("1200x600")

    info_text = tk.StringVar(window)
    testzip_path = tk.StringVar(window)
    q = multiprocessing.Queue()
    p = None

    results_dict = dict()
    reports_dict = dict()

    if testzip:
        path = pathlib.PureWindowsPath(os.path.abspath(testzip)).as_posix()
        testzip_path.set(path)

    setup_frame = tk.Frame(window)
    setup_frame.pack(ipadx=10, ipady=5, fill=tk.X, expand=False, side=tk.TOP)

    progress_frame = tk.Frame(window)
    progress_frame.pack(ipadx=10, ipady=5, fill=tk.X, expand=False, side=tk.BOTTOM)

    info_label = tk.Label(progress_frame, width=200, textvariable=info_text)
    info_label.pack(fill=tk.X, expand=True, side=tk.TOP)

    progress_bar = ttk.Progressbar(
        progress_frame, orient="horizontal", mode="determinate"
    )
    progress_bar.pack(fill=tk.X, expand=True, side=tk.BOTTOM, padx=10)

    info_frame = tk.Frame(window)
    info_frame.pack(ipadx=10, ipady=5, fill=tk.BOTH, expand=True, side=tk.TOP)

    columns = ("test", "runtime")
    task_list = ttk.Treeview(info_frame, columns=columns, selectmode="browse")
    task_list.pack(fill=tk.Y, expand=False, side=tk.LEFT)

    text_area = scrolledtext.ScrolledText(info_frame, wrap=tk.NONE, font="Courier 10")
    text_area.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

    text_area.tag_configure("goodline", background="#DDFFDD")
    text_area.tag_configure("goodchar", background="#99EE99")
    text_area.tag_configure("badline", background="#FFDDDD")
    text_area.tag_configure("badchar", background="#FFAAAA")
    text_area.tag_configure("infoline", background="#FFFFCC")
    text_area.tag_configure(
        "header", background="black", foreground="white", font="Courier 10 bold"
    )
    tag_map = {
        "- ": ("goodline", "goodchar"),
        "+ ": ("badline", "badchar"),
        "? ": ("infoline", None),
        "  ": (None, None),
        GraderTestResult.HEADER_TAG: ("header", None),
    }
    text_area.configure(state=tk.DISABLED)

    task_list.column("#0", minwidth=50, width=50, stretch=False, anchor=tk.CENTER)
    task_list.heading("test", text="Test Name")
    task_list.column("test", minwidth=200, width=200, stretch=False)
    task_list.heading("runtime", text="Runtime")
    task_list.column("runtime", minwidth=80, width=80, stretch=False)

    PASS_ICON = tk.PhotoImage(data=PASS_GIF, format="gif")
    FAIL_ICON = tk.PhotoImage(data=FAIL_GIF, format="gif")
    INFO_ICON = tk.PhotoImage(data=INFO_GIF, format="gif")

    def _add_style_errors(report):
        if report.style_errors:
            label = "<style errors ({count:d})>\n".format(
                count=len(report.style_errors)
            )
            text_area.insert("end", label, ("header",))
            with open(report.source, "r") as f:
                source_lines = f.readlines()

            for line in report.style_errors:
                text_area.insert("end", line + "\n", ("infoline",))
                line_num, col_num = (int(x) for x in line.split(":")[1:3])
                text_area.insert("end", source_lines[line_num - 1])
                for ch in source_lines[line_num - 1][: (col_num - 1)]:
                    text_area.insert("end", ch if ch.isspace() else " ")
                text_area.insert("end", "^\n")

    def _load_result(result):
        text_area.configure(state=tk.NORMAL)
        text_area.delete("1.0", tk.END)

        line_number, highlight = 0, None
        for line in result.get_output():
            pre, msg = line[:2], line[2:]
            if pre == "? ":
                x = None
                for i, ch in enumerate(msg + " "):
                    if x is None and not ch.isspace():
                        x = i
                    elif x is not None and ch.isspace():
                        text_area.tag_add(
                            highlight,
                            "{:d}.{:d}".format(line_number, x),
                            "{:d}.{:d}".format(line_number, i),
                        )
                        x = None
            else:
                this_style, highlight = tag_map[pre]
                text_area.insert("end", msg + "\n", (this_style,))
                line_number += 1
        _add_style_errors(result.report)
        text_area.configure(state=tk.DISABLED)

    def _load_report(report):
        text_area.configure(state=tk.NORMAL)
        text_area.delete("1.0", tk.END)
        if report.errors:
            header = "<syntax and runtime errors ({count:d})>\n".format(
                count=len(report.errors)
            )
            text_area.insert("end", header, ("header",))

            for error in report.errors:
                text_area.insert("end", error, ("infoline",))
                text_area.insert("end", "\n")

        _add_style_errors(report)
        text_area.configure(state=tk.DISABLED)

    def _task_select(event):
        for selected_item in task_list.selection():
            item = task_list.item(selected_item)
            if not item:
                continue

            tag = item["values"][0]
            if tag in results_dict:
                _load_result(results_dict[tag])
            elif tag in reports_dict:
                _load_report(reports_dict[tag])
            return

    task_list.bind("<<TreeviewSelect>>", _task_select)

    task_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=task_list.yview)
    task_list.configure(yscroll=task_scroll.set)
    task_scroll.pack(fill=tk.Y, expand=False, side=tk.LEFT)

    def set_progress(msg, bar):
        progress_bar["value"] = bar
        info_text.set(msg)

    def work_loop():
        def _handle_result(result):
            if result.get_name() in results_dict:
                return
            status = PASS_ICON if result.is_passing() else FAIL_ICON
            task_list.insert(
                "",
                tk.END,
                image=status,
                values=(result.get_name(), "{:.2f} sec".format(result.runtime)),
            )
            results_dict[result.get_name()] = result
            task_list.yview(tk.MOVETO, 1.0)

        def _add_report_notes(report):
            if report.has_errors():
                name = "{source:s}/errors".format(source=report.source)
                task_list.insert("", tk.END, image=INFO_ICON, values=(name, "---"))
                reports_dict[name] = report
                task_list.yview(tk.MOVETO, 1.0)

        nonlocal p
        while not q.empty():
            type, data = q.get_nowait()
            if type == "progress":
                set_progress(*data)
            elif type == "report":
                for result in data.results:
                    _handle_result(result)
                _add_report_notes(data)
            elif type == "result":
                _handle_result(data)
            else:
                p = None
                set_progress(*data)
                return
        window.after(50, work_loop)

    def select_file(types, var):
        def _f():
            var.set(
                filedialog.askopenfilename(
                    filetypes=types, initialdir=os.path.dirname(__file__)
                )
            )

        return _f

    def load_zip():
        nonlocal p
        if p is not None:
            return

        zippath = testzip_path.get()
        if not os.path.exists(zippath):
            info_text.set("Grader test archive not found. Check path and try again.")
            return

        results_dict.clear()
        for item in task_list.get_children():
            task_list.delete(item)

        text_area.configure(state=tk.NORMAL)
        text_area.delete("1.0", tk.END)
        text_area.configure(state=tk.DISABLED)

        work_loop()
        p = multiprocessing.Process(target=_run_tests, args=(zippath, q))
        p.start()

    menu = tk.Menu(window)
    menu.add_command(label="File")

    test_path_label = tk.Label(setup_frame, text="Grader Test Archive")
    test_path_label.pack(fill=tk.NONE, expand=False, side=tk.LEFT, padx=5)

    test_path_input = tk.Entry(setup_frame, textvariable=testzip_path)
    test_path_input.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=5)

    test_path_select_btn = tk.Button(
        setup_frame, text="Choose File", command=select_file(TYPE_ZIP, testzip_path)
    )
    test_path_select_btn.pack(fill=tk.NONE, expand=False, side=tk.LEFT, padx=5)

    test_path_run_btn = tk.Button(setup_frame, text="Run Tests", command=load_zip)
    test_path_run_btn.pack(fill=tk.NONE, expand=False, side=tk.LEFT, padx=5)

    window.state("zoomed")
    if autorun:
        load_zip()  # if there is a zipfile
    window.mainloop()
    if p is not None:
        p.kill()


def main():
    if len(sys.argv) < 2:
        zips = glob.glob("tests-lab*.zip")
        testzip, latest = None, -1
        for z in zips:
            labnum = int(TESTZIP_RE.search(z).group(3))
            if labnum > latest:
                testzip, latest = z, labnum
        if len(zips) > 1:
            print(
                "Found multiple ({:d}) test zips, ignoring all but the most recent one!".format(
                    len(zips)
                )
            )
        if testzip is not None:
            print("Selected {zippath:s} by default...".format(zippath=testzip))
        return test_via_gui(testzip)
    else:
        return test_via_console(sys.argv[1])


if __name__ == "__main__":
    main()
