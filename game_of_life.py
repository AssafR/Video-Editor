import numpy as np
from tkinter import ttk, Tk, Canvas, DISABLED

RECTANGLE_OFFSET = 20
RECTANGLE_SPACE = 4
WORLD_WIDTH = 30
WORLD_HEIGHT = 20
DEFAULT_RECTANGLE_SIZE = 20


def random_world(width, height):
    # Create a random world of width and height consisting of 0/1 in equal probability
    world = ((0.5 + np.random.rand(width, height)).astype('int8'))
    return world


class Board:
    def __init__(self):
        self.root = Tk()
        self.root.title("Game of Life")
        self.root.geometry("800x600")
        self.root.configure(bg='white')

    def board_main(self):
        self.canvas = Canvas(self.root,  # Canvas on which the grid will be displayed
                             width=WORLD_WIDTH * DEFAULT_RECTANGLE_SIZE + 2 * RECTANGLE_OFFSET - 2,
                             height=WORLD_HEIGHT * DEFAULT_RECTANGLE_SIZE + 2 * RECTANGLE_OFFSET - 2,
                             bg='red')
        self.canvas.pack()
        self.btn_next_round = ttk.Button(self.root, text='Next Round', command=self.next_round, state='enabled')
        self.btn_next_round.place(x=100, y=500)
        self.next_round()  # Initialize with a first round
        self.root.mainloop()

    def next_round(self):
        self.calculate_next_round()
        self.draw_world_on_canvas(self.world)

    def calculate_next_round(self):
        # Temporary for development only: Create a new random world
        self.world = random_world(WORLD_WIDTH, WORLD_HEIGHT)

    def draw_world_on_canvas(self, world):  # Paint the world as a grid on the canvas
        width, height = world.shape
        for i in range(width):
            for j in range(height):
                if world[i, j] > 0:
                    fill_color = '#000fff000'  # Green
                else:
                    fill_color = '#000000000'  # Black
                self.canvas.create_rectangle(
                    RECTANGLE_OFFSET + RECTANGLE_SPACE + i * DEFAULT_RECTANGLE_SIZE,
                    RECTANGLE_OFFSET + RECTANGLE_SPACE + j * DEFAULT_RECTANGLE_SIZE,
                    RECTANGLE_OFFSET + RECTANGLE_SPACE + (
                            i + 1) * DEFAULT_RECTANGLE_SIZE - RECTANGLE_SPACE,
                    RECTANGLE_OFFSET + RECTANGLE_SPACE + (
                            j + 1) * DEFAULT_RECTANGLE_SIZE - RECTANGLE_SPACE,
                    fill=fill_color,
                    outline=fill_color
                )


if __name__ == '__main__':
    my_board = Board()
    my_board.board_main()
