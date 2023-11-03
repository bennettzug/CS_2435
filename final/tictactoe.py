"""Solves tictactoe problem on CS 2435 final."""
# take in a board state
# determine if x or o won, if the game is ongoing, or if a tie


def read_board(filename):
    """Provided a filename, returns a board object, represented as a list of 3
    strings, one for each row."""
    with open(filename, encoding="utf-8") as o:
        board = []
        for line in o:
            board.append(line.rstrip().lower())
    return board


def empty_counter(board):
    """Provided a board, returns how many locations are empty ('.')"""
    empty = 0
    for i in board:
        for ch in i:
            if ch == ".":
                empty += 1
    return empty


def print_winner(board):
    """Prints out the winner of a tic tac toe game,
    or whether it is a tie or ongoing."""

    empty = empty_counter(board)
    # check x winning
    if (
        "xxx" in board
        or (board[0][0] + board[1][0] + board[2][0] == "xxx")
        or (board[0][1] + board[1][1] + board[2][1] == "xxx")
        or (board[0][2] + board[1][2] + board[2][2] == "xxx")
        or (board[0][0] + board[1][1] + board[2][2] == "xxx")
        or (board[0][2] + board[1][1] + board[2][0] == "xxx")
    ):
        print("X wins")
    # check o winning
    elif (
        "ooo" in board
        or (board[0][0] + board[1][0] + board[2][0] == "ooo")
        or (board[0][1] + board[1][1] + board[2][1] == "ooo")
        or (board[0][2] + board[1][2] + board[2][2] == "ooo")
        or (board[0][0] + board[1][1] + board[2][2] == "ooo")
        or (board[0][2] + board[1][1] + board[2][0] == "ooo")
    ):
        print("O wins")
    # check tie-ness
    elif empty == 0:
        print("Tie")
    # else game must be ongoing
    else:
        print("Incomplete")


def main():
    """reads in a board from state.txt and prints winner"""
    board = read_board("state.txt")
    print_winner(board)


if __name__ == "__main__":
    main()
