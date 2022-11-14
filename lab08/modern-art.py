'''Solves modern art problem from lab 08'''
import drawBot as messedupdrawbot
# pretty sure something is wrong with the drawbot module.
# this workaround 'fixes' it
# pylint: disable-next=protected-access
drawBot = messedupdrawbot._drawBotDrawingTool


def read_file(filename):
    'takes in file, returns shit idk what yet'
    artwork_list = []
    with open(filename, encoding='utf-8') as artwork_file:
        for line in artwork_file:
            artwork_list.append(line.strip())
    yield artwork_list[0].split()
    for item in artwork_list[1:]:
        yield item.split()


def tuple_from_hex(hexcode: str):
    '''takes in a hexcode string, returns the color as a 3 element tuple
    containing each color, represented as a float from 0 to 1'''
    red = int(hexcode[1:2], base=16) / 25.5
    green = int(hexcode[3:4], base=16) / 25.5
    blue = int(hexcode[5:6], base=16) / 25.5
    return (red, green, blue)


def draw_artwork(filename, output_filename):
    '''takes in a file and outputs the artwork to a new file.'''
    artwork_gen = read_file(filename)
    background = next(artwork_gen)
    drawBot.newDrawing()
    drawBot.newPage(int(background[0]) * 100, int(background[1]) * 100)
    red, green, blue = tuple_from_hex(background[2])
    drawBot.fill(red, green, blue)
    drawBot.rect(
                 0,
                 0,
                 drawBot.width(),
                 drawBot.height())
    for circle in artwork_gen:
        red, green, blue = tuple_from_hex(circle[3])
        drawBot.fill(red, green, blue)
        drawBot.oval(
                     float(circle[0]) * 100,
                     float(circle[1]) * 100,
                     float(circle[2]) * 200,
                     float(circle[2]) * 200)
    drawBot.saveImage(output_filename)
    drawBot.endDrawing()


# class ArtworkBackground:
#     def __init__(self, canvas_x, canvas_y, color) -> None:
#         self.canvas_x = canvas_x
#         self.canvas_y = canvas_y
#         self.color = color

# class ArtworkCircle:
#     def __init__(self, x_location, y_location, radius, color) -> None:
#         self.x_location = x_location
#         self.y_location = y_location
#         self.radius = radius
#         self.color = color


# def create_artwork(Artwork):


def main() -> None:
    '''does all the things, should be pretty readable.'''
    draw_artwork('art.txt', 'art.png')


if __name__ == '__main__':
    main()
