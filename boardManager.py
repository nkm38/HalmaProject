from tkinter import *
import pprint
import time


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
        self.jump = False

        # Used for game-end
        self.winner = 0
        self.coloring = False

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
                valid, jump = self.check_move_validity(i, j)
                if valid:
                    self.move(i, j, jump)

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

    # Blindly checks if the x/y pair is a valid move from the selected piece
    def check_move_validity(self, x, y):
        if self.has_moved and not self.jump:
            return False, False

        # Positive means moving towards zero, negative means away from zero
        deltax = self.selected_x - x
        deltay = self.selected_y - y

        # Is the space empty?
        if self.pieces[x][y] != 0:
            return False, False
        # Is it close enough to at least jump?
        if deltax > 2 or deltax < -2:
            return False, False
        if deltay > 2 or deltay < -2:
            return False, False

        if deltax == 2:
            if deltay == 0 and self.pieces[x + 1][y] != 0:
                return True, True
            elif deltay == -2 and self.pieces[x + 1][y - 1] != 0:
                return True, True
            elif deltay == 2 and self.pieces[x + 1][y + 1] != 0:
                return True, True
            return False, False
        elif deltax == -2:
            if deltay == 0 and self.pieces[x - 1][y] != 0:
                return True, True
            elif deltay == -2 and self.pieces[x - 1][y - 1] != 0:
                return True, True
            elif deltay == 2 and self.pieces[x - 1][y + 1] != 0:
                return True, True
            return False, False
        elif deltax == 0 and deltay != 1 and deltay != -1:
            if deltay == -2 and self.pieces[x][y - 1] != 0:
                return True, True
            elif deltay == 2 and self.pieces[x][y + 1] != 0:
                return True, True
            return False, False

        # Else it's an empty spot 1 space away, so it's a valid move unless we
        # have already done a jump (in which case we are only allowed to jump)
        if self.has_moved and self.jump:
            return False, False
        return True, False

    # Blindly move the selected piece to the given x/y pair
    def move(self, x, y, jumped):
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
        self.jump = jumped

    def end_turn(self):
        # Reset all of our variables for the next player
        self.has_moved = False
        self.jump = False
        if self.active_player == 1:
            self.active_player = 2
            self.root.wm_title("Halma Game: Player 2 to Move")
        else:
            self.active_player = 1
            self.root.wm_title("Halma Game: Player 1 to Move")

        # Check Player 1 for win condition
        self.winner = 1
        for i in range(0, 4):
            for j in range(0, 4):
                if i + j > 3:
                    continue
                if self.pieces[self.size - 1 - i][j] != 1:
                    self.winner = 0
                    break

        # Check Player 2 for win condition
        self.winner = 2
        for i in range(0, 4):
            for j in range(0, 4):
                if i + j > 3:
                    continue
                if self.pieces[i][self.size - 1 - j] != 2:
                    self.winner = 0
                    break

        # Winner loop if we had one
        if self.winner == 1:
            self.root.wm_title("Halma Game: Player 1 Wins!")
            self.root.after(100, self.win_cycle)
            pp.pprint(self.pieces)

        if self.winner == 2:
            self.root.wm_title("Halma Game: Player 2 Wins!")
            self.root.after(100, self.win_cycle)
            pp.pprint(self.pieces)

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
