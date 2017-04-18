import tkinter as tk


class GameBoard(tk.Frame):
    def __init__(self, parent, rows=16, columns=16, size=250, color1="white", color2="white", pieces=None, picture=None):
        """size is the size of a square, in pixels"""
        # Some vars used in the layout.
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        # This will handle if a pieces dict gets passed in.
        if pieces:
            self.pieces = pieces
        else:
            self.pieces = {}
        # Sets the canvas width and height based on the passed in size.
        canvas_width = columns * size
        canvas_height = rows * size

        tk.Frame.__init__(self, parent)
        # If you dont know what tk.Canvas is be sure to check it out. It makes a lot of harder things very easy!
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=canvas_width, height=canvas_height, background="bisque")
        # Pack the canvas into the frame.
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # this binding will refresh the game board if the user resize the window.
        self.canvas.bind("<Configure>", self.refresh)

    def addpiece(self, name, image, row=0, column=0):
        """Add a piece to the playing board"""
        # Creates the image object to be used by the layout/canvas
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"), anchor="c")
        # Runs placepiece to put the image in the right place.
        self.placepiece(name, row, column)

    def placepiece(self, name, row, column):
        """Place a piece at the given row/column"""
        # Creates an entry in the dictionary to remember where the piece is.
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)

        self.canvas.coords(name, x0, y0)

    def refresh(self, event):
        """Redraw the board, possibly in response to window being resized"""
        # Calculate the new size for the board based on the even information.
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        # Set a new size value.
        self.size = min(xsize, ysize)
        # Essentially this is the process of deleting the canvas and recreating it with the new sizes.
        # This happens so fast that you do not notice it.
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        # Replace the pieces on the board now with the new size.
        for name in self.pieces:
            self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def get_peices(self):
        return self.pieces


if __name__ == "__main__":
    # Create root object.
    root = tk.Tk()
    # Initialize the board with no inputs.
    board = GameBoard(root)
    # Pack the basic board
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    # Load in a 'piece' picture. In this case it is just a black dot.
    player1pieces = tk.PhotoImage(file="blkDot100x100.png")
    # Add 3 pieces to the board. p1, p2 and p3 in the rows and columns given.
    board.addpiece("p3",player1pieces,15,0)  # row 15, col 0
    board.addpiece("p1",player1pieces,15,1)  # row 15, col 1
    board.addpiece("p2",player1pieces,14,0)  # etc.
    # Run the board mainloop
    root.mainloop()
    # get the current boards pieces dictionary
    a = board.get_peices()
    root2 = tk.Tk()
    # Create a new board with the pieces dict as a parameter.
    board2 = GameBoard(root2,pieces=a)
    # pack it
    board2.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    # TESTING: adding a piece to see if it crashes (in this case it does).
    # TODO: If a board pieces dict is passed in, the picture needs to be initialized as well. This could require changing
    # TODO: the current implementation, or finding a creative way to also pass in the PhotoImage object!
    board2.addpiece("p4",player1pieces,5,5)
    root2.mainloop()