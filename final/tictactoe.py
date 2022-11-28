# take in a board state
# determine if x or o won, if the game is ongoing, or if the game resulted in a tie
with open("state.txt") as o:
    board = []
    for line in o:
        board.append(line.rstrip().lower())

# count number of each type
def letterCounter(board):
    x = 0
    o = 0
    empty = 0
    for i in board:
        for ch in i:
            if ch == 'x':
                x += 1
            elif ch == 'o':
                o += 1
            else:
                empty += 1
    return x, o, empty


x, o, empty = letterCounter(board)
# check x winning
if 'xxx' in board \
    or (board[0][0] + board[1][0] + board[2][0] == 'xxx')\
    or (board[0][1] + board[1][1] + board[2][1] == 'xxx')\
    or (board[0][2] + board[1][2] + board[2][2] == 'xxx')\
    or (board[0][0] + board[1][1] + board[2][2] == 'xxx')\
        or (board[0][2] + board[1][1] + board[2][0] == 'xxx'):
    print("X wins")
# check o winning
elif 'ooo' in board \
    or (board[0][0] + board[1][0] + board[2][0] == 'ooo')\
    or (board[0][1] + board[1][1] + board[2][1] == 'ooo')\
    or (board[0][2] + board[1][2] + board[2][2] == 'ooo')\
    or (board[0][0] + board[1][1] + board[2][2] == 'ooo')\
        or (board[0][2] + board[1][1] + board[2][0] == 'ooo'):
    print('O wins')
# check tie-ness
elif empty == 0:
    print('Tie')
# else game must be ongoing
else:
    print('Incomplete')
