"""Solves modern art problem from lab 08"""
import math
from functools import lru_cache
from typing import Tuple, Callable, Generator
from collections import namedtuple
import random
# commmenting this out for now, as importing the module took like .25 secs
# might have thrown an error if it's run on a system where it isn't installed
# import drawBot as messedupdrawbot
# pretty sure something is wrong with the drawbot module,
# this workaround 'fixes' it
# drawBot = messedupdrawbot._drawBotDrawingTool


def tuple_from_hex(hexcode: str):
    """takes in a hexcode string, returns the color as a 3 element tuple
    containing each color, represented as a float from 0 to 1"""
    red = int(hexcode[1:2], base=16) / 25.5
    green = int(hexcode[3:4], base=16) / 25.5
    blue = int(hexcode[5:6], base=16) / 25.5
    return (red, green, blue)


ArtworkCircle = namedtuple("Circle", ["x_location", "y_location", "radius", "color"])

ArtworkBackground = namedtuple("Background", ["canvas_x", "canvas_y", "color"])


class Artwork:
    """class containing methods to deal with the "artwork" file that has been
    provided"""

    def __init__(self, filename) -> None:
        self.filename = filename

    def read_file(self) -> Generator[Tuple, None, None]:
        "generator that yields each line of the file as the correct type"
        artwork_list = []
        with open(self.filename, encoding="utf-8") as artwork_file:
            for line in artwork_file:
                artwork_list.append(line.strip())
        yield ArtworkBackground(*artwork_list[0].split())
        for item in artwork_list[1:]:
            yield ArtworkCircle(*item.split())

    @lru_cache(maxsize=1000)
    def artwork(self) -> Tuple[ArtworkBackground, Tuple[ArtworkCircle, ...]]:
        """returns a tuple of the form (background, (circle0...circleN))"""
        gen = self.read_file()
        background = next(gen)
        circles = []
        for circle in gen:
            circles.append(circle)
        circles = tuple(circles)
        return (background, circles)

    # commented out, as module import took too much time

    # def draw_artwork(self, output_filename):
    #     '''takes in a file and outputs the artwork to a new file.'''
    #     background = self.artwork()[0]
    #     tuple_of_circles = self.artwork()[1]
    #     drawBot.newDrawing()
    #     drawBot.newPage(int(background.canvas_x) * 100,
    #                     int(background.canvas_y) * 100)
    #     drawBot.fill(*tuple_from_hex(background.color))
    #     drawBot.rect(
    #                 0,
    #                 0,
    #                 drawBot.width(),
    #                 drawBot.height())
    #     for circle in tuple_of_circles:
    #         drawBot.fill(*tuple_from_hex(circle.color))
    #         drawBot.oval(
    #                     (float(circle.x_location) -
    #                      float(circle.radius)) * 100,
    #                     (float(circle.y_location) -
    #                      float(circle.radius)) * 100,
    #                     float(circle.radius) * 200,
    #                     float(circle.radius) * 200)
    #     drawBot.saveImage(output_filename)
    #     drawBot.endDrawing()

    def random_x_y(self) -> Tuple:
        """Returns a tuple containing a random point within the canvas."""
        rand_x = random.random() * float(self.artwork()[0].canvas_x)
        rand_y = random.random() * float(self.artwork()[0].canvas_y)
        return (rand_x, rand_y)

    def is_overlapping(self, x, y) -> bool:
        """Returns a boolean value as to whether or not a point
        is inside of one of the circles in the artwork."""
        for circle in self.artwork()[1]:
            distance = math.sqrt(
                (x - float(circle.x_location)) * (x - float(circle.x_location))
                + (y - float(circle.y_location)) * (y - float(circle.y_location))
            )
            if distance <= float(circle.radius):
                return False
        return True

    def overlapping_test(self) -> bool:
        """Runs is_overlapping on a random point in the canvas."""
        return self.is_overlapping(*self.random_x_y())


def bool_repeater(trials: int, function: Callable, success=True) -> float:
    """Repeats a boolean test a certain number of times, then returns the
    success rate."""
    count = 0
    for _ in range(trials):
        if function() == success:
            count += 1
    return count / trials


def main() -> None:
    """does all the things, should be pretty readable."""
    artwork = Artwork("art.txt")
    print(bool_repeater(100_000, artwork.overlapping_test))


if __name__ == "__main__":
    main()
