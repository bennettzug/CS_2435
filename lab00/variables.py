"""defines some variables and then performs operations on them,
 printing out the results."""


def print_math_strings(x, y) -> None:
    """Prints the simple math equations using 2 inputs."""
    print(f"{x} + {y} = {x + y}")
    print(f"{x} - {y} = {x - y}")
    print(f"{x} * {y} = {x * y}")
    print(f"{x} / {y} = {x / y}")
    print(f"{x} % {y} = {x % y}")


def main() -> None:
    """Runs print_math_strings with x, y = 5, 4."""
    x, y = 5, 4
    print_math_strings(x, y)


if __name__ == "__main__":
    main()
