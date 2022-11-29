'''Solves area under curve problem for CS2435 Final.'''
from typing import Callable
import random
import calc


print("Calculate the area under the curve with the Monte Carlo method.")
x1 = int(input("x1 = "))
x2 = int(input("x2 = "))


def create_bounding_box(x_1, x_2, function: Callable):
    y1 = 0
    y2 = 0
    x = x_1
    while x < x_2:
        if function(x) > y2:
            y2 = function(x)
        x += 0.1
    y2 *= 1.1

    x_range = x_2 - x_1
    y_range = y2
    return x_1, x_2, y1, y2, x_range, y_range


def random_point(x_min, x_max, y_min, y_max, x_range, y_range):
    x = (random.random() * (x_range)) + x_min
    y = (random.random() * (y_range))
    return x, y


def is_under_curve(x, y, function):
    return function(x) > y


bounding_box = create_bounding_box(x1, x2, calc.func)

area = (bounding_box[1] - bounding_box[0]) * (bounding_box[3] - bounding_box[2])

TRIALS = 1_000_000
count = 0
for _ in range(TRIALS):
    if is_under_curve(*random_point(*bounding_box), calc.func):
        count += 1
print((count / TRIALS) * area)
