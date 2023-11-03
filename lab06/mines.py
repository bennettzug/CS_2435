"""Solves mines.py problem in lab06."""


def read_board(filename: str) -> list:
    """takes in a board and returms a list."""
    with open(filename, encoding="utf-8") as file:
        board = []
        for line in file:
            line_list = []
            for char in line.rstrip():
                line_list.append(char)
            board.append(line_list)
    return board


def write_output(board: list, filename: str) -> None:
    """Takes a board and writes it to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        for i in board:
            for j in i:
                file.write(str(j))
            file.write("\n")


def is_mine(board: list, row: int, column: int) -> bool:
    """Takes in a board, and a prospective locatuin, and returns whether or not
    that location contains a mine. If the location is not in the board, also
    returns False."""
    try:
        if row < 0 or column < 0:
            return False
        if board[row][column] != "*":
            return False
        return True
    except IndexError:
        return False


def mine_neighbors(board: list, row: int, column: int) -> int:
    """Takes in a board and a location and returns the number of mines that
    that location borders."""
    mines = 0
    if is_mine(board, row, column):
        mines = 9
    else:
        if is_mine(board, row - 1, column - 1):
            mines += 1
        if is_mine(board, row, column - 1):
            mines += 1
        if is_mine(board, row + 1, column - 1):
            mines += 1
        if is_mine(board, row - 1, column):
            mines += 1
        if is_mine(board, row + 1, column):
            mines += 1
        if is_mine(board, row - 1, column + 1):
            mines += 1
        if is_mine(board, row, column + 1):
            mines += 1
        if is_mine(board, row + 1, column + 1):
            mines += 1
    return mines


def update_board(board: list) -> list:
    """Takes in an input board, and returns an output board."""
    num_board = []
    for row, i in enumerate(board):
        row_board = []
        for column, _ in enumerate(i):
            if mine_neighbors(board, row, column) == 0:
                row_board.append(".")
            elif mine_neighbors(board, row, column) == 9:
                row_board.append("*")
            else:
                row_board.append(mine_neighbors(board, row, column))
        num_board.append(row_board)
    return num_board


def main() -> None:
    """Reads an input board from mines.txt, and outputs an output board
    to output.txt"""
    board = read_board("mines.txt")
    num_board = update_board(board)
    write_output(num_board, "output.txt")


if __name__ == "__main__":
    main()
