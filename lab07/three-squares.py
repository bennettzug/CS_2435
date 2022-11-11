import math
from dataclasses import dataclass


@dataclass
class Answer:
    '''Datalass that contains correct answers. Automatically sorts x,y,z.'''
    def __init__(self, n: int, x: int, y: int, z: int):
        self.n = n
        self.x = min(x, y, z)
        self.z = max(x, y, z)
        self.y = x + y + z - self.x - self.z

    def __str__(self):
        return f"{self.n} = {self.x} + {self.y} + {self.z}"

    def _key(self):
        return (self.n, self.x, self.y, self.z)

    def __eq__(self, other):
        if isinstance(other, Answer):
            return self._key() == other._key()
        return NotImplemented

    def __hash__(self):
        return hash(self._key())


def create_roots_set(n: int) -> tuple[int, set]:
    root_n = math.ceil(math.sqrt(n))
    roots = set()
    for i in range(root_n + 1):
        roots.add(i ** 2)
    return root_n, roots


def find_answers(n: int, root_n: int, roots: set) -> list:
    answers = []
    for x in range(root_n + 1):
        for y in range(x, root_n + 1):
            # using x * x instead of x ** 2 because it's much faster
            # (halves program runtime)
            z_sq = n - (x * x) - (y * y)
            if z_sq in roots:
                ans = Answer(n, (x * x), (y * y), z_sq)
                answers_set = set(answers)
                if ans not in answers_set:
                    answers.append(ans)
    return answers


def print_answers(answers: list) -> None:
    for elem in answers:
        print(elem)
    if answers == []:
        print("cannot be represented as the sum of three squares")


def main() -> None:
    print("Find all ways to represent a number as the sum of three squares.")
    n = int(input("Enter a number: "))
    root_n, roots = create_roots_set(n)
    print_answers(find_answers(n, root_n, roots))


if __name__ == "__main__":
    main()
