# pylint: disable=invalid-name
# pylint HATES code that does math things with coordinates and such
'''Solves area under curve problem for CS2435 Final.'''
from typing import Callable
import random
from collections import namedtuple
import calc


BoundingBox = namedtuple("BoundingBox", ['x1', 'x2', 'y1', 'y2'])
Ranges = namedtuple("Ranges", ["x_range", "y_range"])
TRIALS = 10_000


def create_bounding_box(x1, x2, function: Callable) -> BoundingBox:
    '''Creates a box with a max y value for a given range of a function.'''
    y1 = 0
    y2 = 0
    x = x1
    while x < x2:
        if function(x) > y2:
            y2 = function(x)
        x += 0.1
    y2 *= 1.1
    return BoundingBox(x1, x2, y1, y2)


def x_y_range(boundingbox: BoundingBox) -> Ranges:
    '''Returns the ranges of a given bounding box'''
    x_range = boundingbox.x2 - boundingbox.x1
    y_range = boundingbox.y2 - boundingbox.y1
    return Ranges(x_range, y_range)


def random_point(boundingbox: BoundingBox, ranges: Ranges):
    '''Generates a random point within some bounding box.
    Also requires a ranges object, as generating the ranges once
    is much faster than generating every time, and this function is
    designed to be repeated multiple times.'''
    x = (random.random() * (ranges.x_range)) + boundingbox.x1
    y = (random.random() * (ranges.y_range))
    return x, y


def is_under_curve(x: float, y: float, function: Callable[[float], float]):
    '''Determines if a given point is smaller than or greater than a
    function at the same x value.
    Returns True if below, and False if above.'''
    return function(x) > y


def main():
    '''Takes in function (from calc.py) and 2 input x values. Then generates an
    approximate area under the curve of that function within that range.'''
    print("Calculate the area under the curve with the Monte Carlo method.")
    x1 = int(input("x1 = "))
    x2 = int(input("x2 = "))
    bounding_box = create_bounding_box(x1, x2, calc.func)

    ranges = x_y_range(bounding_box)

    area = ranges.x_range * ranges.y_range

    count = 0
    for _ in range(TRIALS):
        if is_under_curve(*random_point(bounding_box, ranges), calc.func):
            count += 1
    print((count / TRIALS) * area)


if __name__ == "__main__":
    main()
