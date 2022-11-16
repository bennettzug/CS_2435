'''takes shape made of multiple circles, comes up with area'''
import random
from collections import namedtuple
from typing import List
import math

Circle = namedtuple('Circle', ["x_location", "y_location", "radius"])

# DONE: create bounding box

# left bound: smallest (circle.x_location - circle.radius)
# right bound: largest (circle.x_location + circle.radius)
# top bound: largest (circle.y_location + circle.radius)
# bottom bound: smallest (circle.y_location - circle.radius)

def create_bounding_box(circle_list: List[Circle]):
    left_bound = None
    right_bound = None
    top_bound = None
    bottom_bound = None
    for circle in circle_list:
        if left_bound is None or left_bound > (circle.x_location - circle.radius):
            left_bound = (circle.x_location - circle.radius)
        if right_bound is None or right_bound < (circle.x_location + circle.radius):
            right_bound = (circle.x_location + circle.radius)
        if top_bound is None or top_bound < (circle.y_location + circle.radius):
            top_bound = (circle.y_location + circle.radius)
        if bottom_bound is None or bottom_bound > (circle.y_location - circle.radius):
            bottom_bound = (circle.y_location - circle.radius)
    return left_bound, right_bound, bottom_bound, top_bound


# DONE: generate point within bounding box

def random_point(x_min, x_max, y_min, y_max):
    x = random.uniform(x_min, x_max)
    y = random.uniform(y_min, y_max)
    return x, y


# TODO: test if point is inside at least one of the circles

def is_overlapping(x, y, circle_list) -> bool:
    '''Returns a boolean value as to whether or not a point
    is inside of one of the circles in the artwork.'''
    for circle in circle_list:
        distance = math.sqrt((x - float(circle.x_location)) *
                             (x - float(circle.x_location)) +
                             (y - float(circle.y_location)) *
                             (y - float(circle.y_location)))
        if distance <= float(circle.radius):
            return True
    return False


def main():
    circles = [Circle(0, 0, 10), Circle(8, 8, 3), Circle(-8, 8, 3)]
    bounding_box = create_bounding_box(circles)

    circle_area = (bounding_box[1] - bounding_box[0]) * (bounding_box[3] - bounding_box[2])
    
    
    TRIALS = 1_000_000
    count = 0
    for _ in range(TRIALS):
        if is_overlapping(*random_point(*bounding_box), circles):
            count += 1
    print((count / TRIALS) * circle_area)

if __name__ == "__main__":
    main()
