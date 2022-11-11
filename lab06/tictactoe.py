# take in a board state
# determine if x or o won, if the game is ongoing, if the game resulted in a tie, or if it is an invalid board state
o = open("tic.txt", 'r')
board = []
for line in o:
    board.append(line.rstrip().lower())
o.close()
print(board)
# count number of each type
def letterCounter(board):
    x=0
    o=0
    empty=0
    for i in board:
        for ch in i:
            if ch == 'x':
                x += 1
            elif ch == 'o':
                o += 1
            else:
                empty += 1
    return x, o, empty

x,o,empty = letterCounter(board)
#check validity (wrong number of pieces/player)
if not -1 < x-o < 1:
    print("games invalid")
# check x winning
elif 'xxx' in board \
    or (board[0][0] + board[1][0] + board[2][0] == 'xxx')\
         or (board[0][1] + board[1][1] + board[2][1] == 'xxx')\
             or (board[0][2] + board[1][2] + board[2][2] == 'xxx')\
                 or (board[0][0] + board[1][1] + board[2][2] == 'xxx')\
                     or (board[0][2] + board[1][1] + board[2][0] == 'xxx'):
    print("X Won")
# check o winning
elif 'ooo' in board \
    or (board[0][0] + board[1][0] + board[2][0] == 'ooo')\
         or (board[0][1] + board[1][1] + board[2][1] == 'ooo')\
             or (board[0][2] + board[1][2] + board[2][2] == 'ooo')\
                 or (board[0][0] + board[1][1] + board[2][2] == 'ooo')\
                     or (board[0][2] + board[1][1] + board[2][0] == 'ooo'):
    print('O Won')
# check tie-ness
elif empty == 0:
    print('game is a tie')
# else game must be ongoing
else:
    print('games ongoing')
