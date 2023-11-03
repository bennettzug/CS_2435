"""Solves chess.py problem from lab06."""


def read_board(filename) -> list:
    """Takes in a file, retuns a chess board."""
    with open(filename, encoding="utf-8") as file:
        board = []
        for line in file:
            board.append(line.rstrip())
        file.close()
    return board


def loc(board, y, x) -> bool:
    """Takes in a possible location, passes it through if it is valid, and
    returns false if not."""
    if -1 < y < 8 and -1 < x < 8:
        return board[y][x]
    return False


def pawn_tester(board, y, x) -> bool:
    """Takes in the location of a piece and determines if it is being
    attacked by a pawn, returning a bool."""
    return loc(board, y + 1, x + 1) == "P" or loc(board, y + 1, x - 1) == "P"


def knight_tester(board, y, x) -> bool:
    """Takes in the location of a piece and determines if it is being
    attacked by a knight, returning a bool."""
    return (
        loc(board, y + 1, x + 2) == "N"
        or loc(board, y + 2, x + 1) == "N"
        or loc(board, y + 2, x - 1) == "N"
        or loc(board, y + 1, x - 2) == "N"
        or loc(board, y - 1, x - 2) == "N"
        or loc(board, y - 2, x - 1) == "N"
        or loc(board, y - 2, x + 1) == "N"
        or loc(board, y - 1, x + 2) == "N"
    )


def king_tester(board, y, x) -> bool:
    """Takes in the location of a piece and determines if it is being
    attacked by a king, returning a bool."""
    return (
        loc(board, y - 1, x - 1) == "K"
        or loc(board, y - 1, x) == "K"
        or loc(board, y - 1, x + 1) == "K"
        or loc(board, y, x - 1) == "K"
        or loc(board, y, x + 1) == "K"
        or loc(board, y + 1, x - 1) == "K"
        or loc(board, y + 1, x) == "K"
        or loc(board, y + 1, x + 1) == "K"
    )


def projecting_piece_tester(
    board: list, y: int, x: int, y_activator: int, x_activator: int, piece: str
) -> bool:
    """Needs a lengthy doc string to define usage here."""
    adder = 1
    while loc(board, y + (y_activator * adder), x + (x_activator * adder)) == ".":
        adder += 1
    if loc(board, y + (y_activator * adder), x + (x_activator * adder)) == piece:
        return True
    return False


def rook_tester(board, y, x) -> bool:
    """Takes in the location of a piece and determines if it is being
    attacked by a rook, returning a bool."""
    if projecting_piece_tester(board, y, x, 0, 1, "R"):
        return True
    if projecting_piece_tester(board, y, x, 0, -1, "R"):
        return True
    if projecting_piece_tester(board, y, x, 1, 0, "R"):
        return True
    if projecting_piece_tester(board, y, x, -1, 0, "R"):
        return True
    return False


def bishop_tester(board, y, x) -> bool:
    """Takes in the location of a piece and determines if it is being
    attacked by a bishop, returning a bool."""
    if projecting_piece_tester(board, y, x, 1, 1, "B"):
        return True
    if projecting_piece_tester(board, y, x, 1, -1, "B"):
        return True
    if projecting_piece_tester(board, y, x, -1, 1, "B"):
        return True
    if projecting_piece_tester(board, y, x, -1, -1, "B"):
        return True
    return False


def queen_tester(board, y, x) -> bool:
    """Takes in the location of a piece and determines if it is being
    attacked by a queen, returning a bool."""
    return (
        projecting_piece_tester(board, y, x, 0, 1, "Q")
        or projecting_piece_tester(board, y, x, 0, -1, "Q")
        or projecting_piece_tester(board, y, x, 1, 0, "Q")
        or projecting_piece_tester(board, y, x, -1, 0, "Q")
        or projecting_piece_tester(board, y, x, 1, -1, "Q")
        or projecting_piece_tester(board, y, x, -1, -1, "Q")
        or projecting_piece_tester(board, y, x, 1, 1, "Q")
        or projecting_piece_tester(board, y, x, -1, 1, "Q")
    )


def king_finder(board: list) -> tuple[int, int]:
    """Takes in the board, and returns the position of the black king."""
    king_y = 0
    king_x = 0
    for i, elem in enumerate(board):
        if elem.find("k") != -1:
            king_x = elem.find("k")
            king_y = i
    return king_y, king_x


def bk_in_check(board):
    """Takes in a board, and determines if the black king is in check."""
    king_y, king_x = king_finder(board)
    return (
        pawn_tester(board, king_y, king_x)
        or knight_tester(board, king_y, king_x)
        or king_tester(board, king_y, king_x)
        or rook_tester(board, king_y, king_x)
        or bishop_tester(board, king_y, king_x)
        or queen_tester(board, king_y, king_x)
    )


def main():
    """Generates board from file, then determines if black king is in check,
    and prints out the answer"""
    board = read_board("chess.txt")
    isisnot = "" if bk_in_check(board) else "not "
    print(f"Black king is {isisnot}in check.")


if __name__ == "__main__":
    main()
