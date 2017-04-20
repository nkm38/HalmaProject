from tkinter import *


class GameBoard(Frame):
    def __init__(self, root, size=8, color1="green", color2="red", pieces=None):
        """size is the size of a square, in pixels"""
        self.root = root

        if size not in [8, 10, 15]:
            raise ValueError("Invalid size for board. Please enter 8, 10 or 15")
        # Some vars used in the layout.
        self.size = size
        self.color1 = color1
        self.color2 = color2
        # Buttons dictionary that will be accessed based on a string representation of the buttons location
        # Ex: "12" is a button in row 1 column 2.
        self.buttons = {}
        # This will handle if a pieces dict gets passed in. This might need to be changed depending on how we want to
        # implement the storage of player pieces.
        if pieces:
            self.pieces = pieces
        else:
            self.pieces = {}
        # Initialize the frame.
        Frame.__init__(self, root)
        # Build the board of buttons.
        self.build_board()

    def build_board(self):
        # Builds the board of buttons based on the size passed in to the init.
        for i in range(0, self.size):
            for j in range(0, self.size):
                Grid.columnconfigure(self.root, i, weight=1)
                Grid.rowconfigure(self.root, j, weight=1)
                tmp = Button(self.root, command=self.get_pieces(), height=10, width=10)
                self.buttons[str(i) + str(j)] = tmp
                tmp.grid(row=i, column=j, sticky=N+S+E+W)

        print(self.buttons)

    def get_pieces(self):
        return self.pieces


if __name__ == "__main__":
    # Create root object.
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    # Initialize the board with no inputs.
    board = GameBoard(root)
    # Run the board mainloop
    root.mainloop()