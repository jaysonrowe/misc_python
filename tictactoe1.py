from random import *
from string import *


## Constants ##

EMPTY = ' '     # the value of an empty square
PL_1 = 'x'      # player 1's mark
PL_2 = 'o'      # player 2's mark

A = 'A'     # these just make it easier to keep referring to 'A', 'B' and 'C'
B = 'B'
C = 'C'


## State variables ##

board = [[EMPTY, EMPTY, EMPTY],     # board is initially all empty squares,
         [EMPTY, EMPTY, EMPTY],     # implemented as a list of rows,
         [EMPTY, EMPTY, EMPTY]]     # three rows with three squares each

current_player = randint(1, 2)      # randomly choose starting player


## Coordinate system functions ##

def square(row, col):       # squares are represented as tuples of (row, col).
    return (row, col)       # rows are numbered 1 thru 3, cols 'A' thru 'C'.

def square_row(square):     # these two functions save us the hassle of using
    return square[0]        # index values in our code, e.g. square[0]...

def square_col(square):     # from this point on, i should never directly use
    return square[1]        # tuples when working with squares.

def get_square(square):
    """ Returns the value of the given square. """
    row_i = square_row(square) - 1      # from values of 1-3 to values of 0-2
    col_i = ord(square_col(square)) - ord(A)    # ord gives the ASCII number
                                                # (search ASCII on wikipedia!)
    return board[row_i][col_i]  # note how this and set_square are the ONLY
                                # functions which directly use board!

def set_square(square, mark):
    """ Sets the value of the given square. """
    row_i = square_row(square) - 1
    col_i = ord(square_col(square)) - ord(A)
    board[row_i][col_i] = mark  # note how this and get_square are the ONLY
                                # functions which directly use board!

def get_row(row):
    """ Returns the given row as a list of three values. """
    return [get_square((row, A)), get_square((row, B)), get_square((row, C))]

def get_column(col):
    """ Returns the given column as a list of three values. """
    return [get_square((1, col)), get_square((2, col)), get_square((3, col))]

def get_diagonal(corner_square):
    """ Returns the diagonal that includes the given corner square.
    Only (1, A), (1, C), (3, A) and (3, C) are corner squares. """
    if corner_square == (1, A) or corner_square == (3, C):
        return [get_square((1, A)), get_square((2, B)), get_square((3, C))]
    else:
        return [get_square((1, C)), get_square((2, B)), get_square((3, A))]


## Game logic functions ##

def get_mark(player):
    """ Returns the mark of the given player (1 or 2). """
    if player == 1:
        return PL_1
    else:
        return PL_2

def all_squares_filled():
    """ Returns True iff all squares have been filled. """
    for row in range(1, 4):     # range(1, 4) returns the list [1, 2, 3]
        if EMPTY in get_row(row):
            return False    # this row contains an empty square, we know enough
    return True     # no empty squares found, all squares are filled

def player_has_won(player):
    """ Returns True iff the given player (1 or 2) has won the game. """

    # we need to check if there are three of the player's marks in a row,
    # so we'll keep comparing against a list of three in a row.
    MARK = get_mark(player)
    win = [MARK, MARK, MARK]

    # first check horizontal rows
    if get_row(1) == win or get_row(2) == win or get_row(3) == win:
        return True

    # no horizontal row, let's try vertical rows
    if get_column(A) == win or get_column(B) == win or get_column(C) == win:
        return True

    # no vertical either, let's try the diagonals
    if get_diagonal((1, A)) == win or get_diagonal((1, C)) == win:
        return True

    return False    # none of the above, player hasn't won


## Display functions ##

## How the grid will look
#
#      A   B   C
#                
# 1      |   |  
#     ---+---+---
# 2      |   |   
#     ---+---+---
# 3      |   |   
#

def draw_board_straight():
    """ Returns a straight string representation of the board. """

    # for ease, we'll define all the squares as constants
    A1, A2, A3 = get_square((1, A)), get_square((2, A)), get_square((3, A))
    B1, B2, B3 = get_square((1, B)), get_square((2, B)), get_square((3, B))
    C1, C2, C3 = get_square((1, C)), get_square((2, C)), get_square((3, C))
    
    lines = []
    lines.append("")
    lines.append("     " + A + "   " + B + "   " + C + " ")
    lines.append("              ")
    lines.append("1    " + A1 + " | " + B1 + " | " + C1 + " ")
    lines.append("    ---+---+---")
    lines.append("2    " + A2 + " | " + B2 + " | " + C2 + " ")
    lines.append("    ---+---+---")
    lines.append("3    " + A3 + " | " + B3 + " | " + C3 + " ")
    lines.append("")
    
    return join(lines, '\n')    # the '\n' represents a newline


def draw_board():
    """ Returns a string representation of the board in its current state. """
    return draw_board_straight()  
                                    


## Game functions ##

def reset_board():
    for row in (1, 2, 3):
        for col in (A, B, C):
            set_square(square(row, col), EMPTY)

def play_game():

    global current_player   # we need the global statement to change variables
                            # that are defined OUTSIDE of the current function

    reset_board()
    current_player = randint(1, 2)

    print "Tic-Tac-Toe!"
    print

    player1_name = raw_input("Player 1, what is your name? ")
    player2_name = raw_input("Player 2, what is your name? ")

    # quick helper function to print the given player's name
    def get_name(player):
        if player == 1:
            return player1_name
        else:
            return player2_name

    print
    print "Welcome,", player1_name, "and", player2_name + "!"
    print player1_name, "will be", PL_1 + ", and", player2_name, "will be", PL_2 + "."
    print "By random decision,", get_name(current_player), "will go first."
    print

    raw_input("[Press enter when ready to play.] ")     # just waiting for them to press enter

    print draw_board()

    while not all_squares_filled():

        choice = raw_input(get_name(current_player) + ", which square? (e.g. 2B, 2b, B2 or b2) ")

        if len(choice) != 2:
            print "That's not a square. You must enter a square like b2, or 3C."
            print
            continue

        if choice[0] not in ["1", "2", "3"] and upper(choice[0]) not in [A, B, C]:
            print "The first character must be a row (1, 2 or 3) or column (A, B or C)."
            print
            continue

        if choice[1] not in ["1", "2", "3"] and upper(choice[1]) not in [A, B, C]:
            print "The second character must be a row (1, 2 or 3) or column (A, B or C)."
            print
            continue

        if choice[0] in ["1", "2", "3"] and choice[1] in ["1", "2", "3"]:
            print "You entered two rows! You must enter one row and one column (A, B or C)."
            print
            continue

        if upper(choice[0]) in [A, B, C] and upper(choice[1]) in [A, B, C]:
            print "You entered two columns! You must enter one row (1, 2 or 3) and one column."
            print
            continue

        # if we're here, we have one row and one column, figure out which is which
        if choice[0] in ["1", "2", "3"]:
            row = int(choice[0])
            col = upper(choice[1])
        else:
            row = int(choice[1])
            col = upper(choice[0])

        choice = square(row, col)   # make this into a (row, col) tuple

        if get_square(choice) != EMPTY:
            print "Sorry, that square is already marked."
            print
            continue

        # if we're here, then it's a valid square, so mark it
        set_square(choice, get_mark(current_player))

        print draw_board()

        if player_has_won(current_player):
            print "Congratulations", get_name(current_player), "-- you rock!"
            print
            break

        if all_squares_filled():
            print "Cats game!", player1_name, "and", player2_name, "draw."
            print
            break

        # now switch players
        current_player = 3 - current_player     # sets 1 to 2 and 2 to 1

    print "GAME OVER"
    print


## Main program code ##

if __name__ == "__main__":

    keep_playing = True

    while keep_playing:

        play_game()
        again = lower(raw_input("Play again? (y/n) "))

        print
        print
        print

        if again != "y":
            keep_playing = False

    print "Thanks for playing!"
    print