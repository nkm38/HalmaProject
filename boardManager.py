from tkinter import *
import pprint
import time
import copy

from skynet import alphabeta_search

class Move:
    def __init__(self, start, end):
        self.start_x, self.start_y = start
        self.end_x, self.end_y = end


class GameBoard(Frame):
    def __init__(self, root, size=8, color1="green", color2="red",
                 pieces=None):
        """size is the size of a square, in pixels"""
        self.root = root

        if size not in [8, 10, 15]:
            raise ValueError(
                "Invalid size for board. Please enter 8, 10 or 15")
        # Some vars used in the layout.
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.color3 = "yellow"
        # Buttons dictionary of dictionaries representing x/y from top left
        self.buttons = {}
        # Used to tell if a piece is currently selected
        self.piece_selected = False
        self.selected_x = -1
        self.selected_y = -1
        # Current player's turn, green (1) goes first
        self.active_player = 1
        self.has_moved = False

        # Used for game-end
        self.first_move = True
        self.winner = 0
        self.coloring = False

        self.camps = {}
        for i in range(0, self.size):
            self.camps[i] = {}
            for j in range(0, self.size):
                self.camps[i][j] = False
        for i in range(0,4):
            for j in range(0, 4):
                if i + j > 3:
                    continue
                # Red goal camp
                self.camps[i][self.size - 1 - j] = 2
                # Green goal camp
                self.camps[self.size - 1 - i][j] = 1


        # This will handle if a pieces dict gets passed in. This might need to
        #  be changed depending on how we want to implement the storage of
        #  player pieces.
        if pieces:
            self.pieces = pieces
        else:
            # No board was passed in so set up the default one
            self.pieces = {}
            # Initialize all of the board positions to 0
            for i in range(0, self.size):
                self.pieces[i] = {}
                for j in range(0, self.size):
                    self.pieces[i][j] = 0

            # Then build the camps
            for i in range(0, 4):
                for j in range(0, 4):
                    if i + j > 3:
                        continue
                    # Green camp
                    self.pieces[i][self.size - 1 - j] = 1
                    # Red camp
                    self.pieces[self.size - 1 - i][j] = 2

        self.build_board()

    # Initialize the frame.
    # Build the board of buttons.
    def build_board(self):
        # Board frame
        frame = Frame(self.root)
        frame.grid(row=0, column=0, sticky=N + S + E + W)

        # Set up the grid of buttons
        for i in range(0, self.size):
            Grid.rowconfigure(frame, i, weight=1)
            self.buttons[i] = {}
            for j in range(0, self.size):
                Grid.columnconfigure(frame, j, weight=1)
                btn = Label(frame, height=10, width=10, borderwidth=2,
                            relief="sunken")
                # i is the x coord so is columns here
                btn.grid(row=j, column=i, stick=N + S + E + W)
                self.buttons[i][j] = btn

                # Link each button to a handler event that passes in the x/y
                # coordinates of the button that was pressed
                def handler(event, self=self, i=i, j=j):
                    return self.buttonclick(event, i, j)

                btn.bind('<Button-1>', handler)

        # Then build the camps
        for i in range(0, 4):
            for j in range(0, 4):
                if i + j > 3:
                    continue
                # Green camp
                self.buttons[i][self.size - 1 - j].configure(borderwidth=8,
                                                             relief="raised")
                # Red camp
                self.buttons[self.size - 1 - i][j].configure(borderwidth=8,
                                                             relief="raised")

        # Color our buttons
        for i in range(0, self.size):
            for j in range(0, self.size):
                if self.pieces[i][j] == 1:
                    self.buttons[i][j].configure(bg=self.color1)
                elif self.pieces[i][j] == 2:
                    self.buttons[i][j].configure(bg=self.color2)

    # The actual meat of our program, the button click events
    def buttonclick(self, event, i, j):
        if self.winner != 0:
            return
        if not self.piece_selected:
            if self.pieces[i][j] == self.active_player:
                self.select_button(i, j)
        else:
            if i == self.selected_x and j == self.selected_y:
                self.deselect_button(i, j)
                if self.has_moved:
                    self.end_turn()
            else:
                # Modified to allow use of our find_move method.
                if not self.has_moved:
                    # Find all possible moves for the selected button piece.
                    possible_moves = self.find_moves(self.selected_x,
                                                     self.selected_y)
                    # If the move-to click is a valid possible move, move the piece there.
                    if (i, j) in possible_moves:
                        self.move(i, j)

    # Blindly selects a button
    def select_button(self, x, y):
        self.selected_x = x
        self.selected_y = y
        self.piece_selected = True
        self.buttons[x][y].configure(bg=self.color3)

    # Blindly deselects a button
    def deselect_button(self, x, y):
        self.selected_x = -1
        self.selected_y = -1
        self.piece_selected = False
        if self.pieces[x][y] == 1:
            self.buttons[x][y].configure(bg=self.color1)
        elif self.pieces[x][y] == 2:
            self.buttons[x][y].configure(bg=self.color2)

    def is_valid_space(self, player, startx, starty, x, y):
        """Validates if the space x,y is a valid space on the board.
        Returns True if x and y are on the board,
        False otherwise."""

        if x < 0 or y < 0:
            return False
        if x >= self.size or y >= self.size:
            return False
        if self.camps[startx][starty] == player and self.camps[x][y] != player:
            return False
        return True

    def find_moves(self, x, y):
        """Find all possible moves for a piece located at x,y. If there is a possible jump, this method calls
        recursive_jump_detector to see if there are any further jumps after that move.
        Returns a moveset set that contains all possible moves that piece can make."""

        moveset = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if not self.is_valid_space(self.active_player, x, y, x + i, y + j):
                    continue
                if self.pieces[x + i][y + j] == 0:
                    moveset.add((x + i, y + j))
                else:
                    if self.is_valid_space(self.active_player, x, y, x + i * 2, y + j * 2) and \
                                    self.pieces[x + 2 * i][y + 2 * j] == 0:
                        moveset.add((x + i * 2, y + j * 2))
                        self.recursive_jump_detector(moveset, x + i * 2,
                                                     y + j * 2)
        return moveset

    def recursive_jump_detector(self, moveset, x, y):
        """A recursive method that will find all possible jumps from a given x,y. Takes a moveset to avoid infinite
        recursion on places it has already visited.
        The recursive method mutates the variable moveset as it moves downward. It does not return anything."""

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if not self.is_valid_space(self.active_player, x, y, x + i, y + j):
                    continue
                if self.pieces[x + i][y + j] != 0:
                    if self.is_valid_space(self.active_player, x, y, x + i * 2, y + j * 2) and \
                          self.pieces[x + i * 2][y + j * 2] == 0 and \
                          (x + i * 2, y + j * 2) not in moveset:
                        moveset.add((x + i * 2, y + j * 2))
                        self.recursive_jump_detector(moveset, x + i * 2,
                                                     y + j * 2)

    # Blindly move the selected piece to the given x/y pair
    def move(self, x, y):
        # First move the piece data
        self.pieces[x][y] = self.active_player
        self.pieces[self.selected_x][self.selected_y] = 0

        # Now move the button appearance
        self.buttons[self.selected_x][self.selected_y].configure(bg="white")
        self.buttons[x][y].configure(bg=self.color3)

        # Update selected_x/y
        self.selected_x = x
        self.selected_y = y

        # And set has_moved and jump
        self.has_moved = True

    def end_turn(self):
        # Reset all of our variables for the next player
        self.has_moved = False
        if self.active_player == 1:
            self.active_player = 2
            self.root.wm_title("Halma Game: Player 2 to Move")
        else:
            self.active_player = 1
            self.root.wm_title("Halma Game: Player 1 to Move")
        # Check to see if there is a winner.
        self.winner = self.win_check()
        # If there was a winner, then prompt who won.
        if self.winner == 1:
            self.root.wm_title("Halma Game: Player 1 Wins!")
            self.root.after(100, self.win_cycle)
            pp.pprint(self.pieces)

        if self.winner == 2:
            self.root.wm_title("Halma Game: Player 2 Wins!")
            self.root.after(100, self.win_cycle)
            pp.pprint(self.pieces)
        # If it is the first move, and the active player is 2, then we can set
        # the first_move flag to False. This way, the initial board layout
        #  doesn't count as a win.
        if self.first_move and self.active_player == 2:
            self.first_move = False

    # Verify if there is a winner based on the blocks in the winner areas. If
    # they are full, then one of the two players have won.
    def win_check(self, check_board=None):
        if check_board:
            board = check_board
        else:
            board = self.pieces

        if self.first_move:
            return 0
        # Check Player 1 space for win condition
        check = 1
        for i in range(0, 4):
            for j in range(0, 4):
                if i + j > 3:
                    continue
                if board[self.size - 1 - i][j] == 0:
                    check = 0
                    break
        if check == 1:
            return check
        # Check Player 2 space for win condition
        check = 2
        for i in range(0, 4):
            for j in range(0, 4):
                if i + j > 3:
                    continue
                if board[i][self.size - 1 - j] == 0:
                    check = 0
                    break
        if check == 2:
            return check
        else:
            return 0

    def win_cycle(self):
        # Fancy flashing end screen
        if self.winner == 1:
            if not self.coloring:
                self.coloring = True
                for j in range(3, -1, -1):
                    for i in range(0, 4):
                        if i + j > 3:
                            continue
                        self.buttons[i][self.size - 1 - j].configure(
                            bg=self.color3)
                        time.sleep(.1)
                        self.root.update_idletasks()
            else:
                self.coloring = False
                for j in range(3, -1, -1):
                    for i in range(0, 4):
                        if i + j > 3:
                            continue
                        self.buttons[i][self.size - 1 - j].configure(
                            bg=self.color1)
                        time.sleep(.1)
                        self.root.update_idletasks()
        if self.winner == 2:
            if not self.coloring:
                self.coloring = True
                for j in range(3, -1, -1):
                    for i in range(0, 4):
                        if i + j > 3:
                            continue
                        self.buttons[i][self.size - 1 - j].configure(
                            bg=self.color3)
                        time.sleep(.1)
                        self.root.update_idletasks()
            else:
                self.coloring = False
                for j in range(3, -1, -1):
                    for i in range(0, 4):
                        if i + j > 3:
                            continue
                        self.buttons[i][self.size - 1 - j].configure(
                            bg=self.color2)
                        time.sleep(.1)
                        self.root.update_idletasks()
        self.root.after(100, self.win_cycle)

    def get_pieces(self):
        return self.pieces

    def heuristic(self):
        # TODO: Build heuristic function
        return 1

    def generate_future_board(self, movelist):
        """Generates a future board based on a movelist.
        will run through each move in the movelist exhaustively, making modifications
        to a deep copy of the current game board.
        returns a dictionary of the future board."""

        # Movelist: A list of move objects that we can use to generate a future board.
        future_board = copy.deepcopy(self.pieces)
        for move in movelist:
            current_piece = future_board[move.start_x][move.start_y]
            future_board[move.start_x][move.start_y] = 0
            future_board[move.end_x][move.end_y] = current_piece
        return future_board

    def successors(self):
        "Return a list of legal (move, state) pairs."
        successors = []
        for i in range(self.size):
            for j in range(self.size):
                if self.pieces[i][j] != 0:
                    for move in self.find_moves(i, j):
                        move_ = Move((i, j), move)
                        successors.append((move_, self.generate_future_board([move_])))
        return successors


if __name__ == "__main__":
    pp = pprint.PrettyPrinter()
    # Create root object.
    root = Tk()
    root.configure(bg="white")
    root.wm_title("Halma Game: Player 1 to Move")
    Grid.rowconfigure(root, 0, weight=1)
    Grid.columnconfigure(root, 0, weight=1)
    # Initialize the board with no inputs.
    board = GameBoard(root)
    # Run the board mainloop
    root.mainloop()

# Testing board for win animation
# {0: {0: 1, 1: 1, 2: 0, 3: 2, 4: 0, 5: 2, 6: 2, 7: 2},
# 1: {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 2, 7: 2},
# 2: {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 2, 7: 2},
# 3: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 2},
# 4: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
# 5: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
# 6: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1},
# 7: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1}}
