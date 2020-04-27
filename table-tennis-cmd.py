import curses
import numpy as np
# from enum import Enum, auto


# class HorizontalAlignment(Enum):
#     LEFT = auto()
#     CENTER = auto()
#     RIGHT = auto()
#
#
# class VerticalAlignment(Enum):
#     TOP = auto()
#     CENTER = auto()
#     BOTTOM = auto()


class Helpers:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    # Top-left corner of window
    @property
    def window_min(self):
        return np.array(self.stdscr.getbegyx())

    # Size of the window - number of rows and columns in the window
    @property
    def window_size(self):
        return np.array(self.stdscr.getmaxyx())

    # Bottom-right corner of window
    @property
    def window_max(self):
        return self.window_min + self.window_size - 1

    # Output the given character at the specified positions
    # Positions is expected to be a NumPy array of shape (N, 2), where N is the number of positions
    def add_chars(self, positions, char):
        for position in positions:
            self.stdscr.addch(position[0], position[1], char)

    # def align(self, object_size, horizontal_alignment=HorizontalAlignment.LEFT,
    #           vertical_alignment=VerticalAlignment.TOP):
    #     if vertical_alignment == VerticalAlignment.BOTTOM:
    #         vertical_position = self.window_max[0] - object_size[0] + 1
    #     elif vertical_alignment == VerticalAlignment.CENTER:
    #         vertical_position = self.center(object_size)[0]
    #     else:
    #         vertical_position = 0
    #
    #     if horizontal_alignment == HorizontalAlignment.RIGHT:
    #         horizontal_position = self.window_max[1] - object_size[1] + 1
    #     elif horizontal_alignment == HorizontalAlignment.CENTER:
    #         horizontal_position = self.center(object_size)[1]
    #     else:
    #         horizontal_position = 0
    #
    #     return np.array((vertical_position, horizontal_position))

    def center(self, object_size):
        return self.window_min + ((self.window_size - 1) // 2) - (object_size // 2)

    def right_align(self, object_size):
        return self.window_max - object_size + 1

    # Convert a 2D NumPy array into a set of tuples
    # Each row in the array becomes a tuple
    @staticmethod
    def convert_to_tuple_set(array):
        return set(map(tuple, array))


# class Ball:
#     def __init__(self, stdscr, initial_position, initial_velocity):
#         self.stdscr = stdscr
#         self.position = initial_position
#         self.velocity = initial_velocity
#
#     def update(self):
#         self.position = self.get_next_position()
#
#     def draw(self):
#         self.stdscr.addch(self.position[0], self.position[1], "O")
#
#     def get_next_position(self):
#         return self.position + self.velocity


# TODO: Consistency with using / not using window_min instead of 0
# TODO: Put this into a Python package at some point
class GameObject:
    # TODO: Allow aligning
    def __init__(self, stdscr, helpers, shape, char):
        self.stdscr = stdscr
        self.helpers = helpers
        self.position = np.array([0, 0])
        self.velocity = np.array([0, 0])
        self.shape = shape
        self.char = char

    @property
    def next_position(self):
        return self.position + self.velocity

    @property
    def size(self):
        return self.shape.max(0) - self.shape.min(0) + 1

    def update(self):
        self.position = self.next_position

    def draw(self):
        for world_point in self.position + self.shape:
            self.helpers.stdscr.addch(world_point[0], world_point[1], self.char)

    def collides_with(self, other):
        self_world_points = self.next_position + self.shape
        other_world_points = other.next_position + other.shape

        return not Helpers.convert_to_tuple_set(self_world_points)\
            .isdisjoint(Helpers.convert_to_tuple_set(other_world_points))

    # Checks whether the entire shape will be within the window, based on the *next* position
    @property
    def is_within_window(self):
        return (self.next_position + self.shape >= np.array([0, 0])).all() \
               and (self.next_position + self.shape < self.helpers.window_size).all()

    @classmethod
    def create_point(cls, stdscr, helpers, char):
        return cls(stdscr, helpers, np.array([[0, 0]]), char)

    # TODO: Potentially generalise to allow diagonal lines too (i.e. lines of any gradient)
    # TODO: Potentially could do collision check using formula instead of with rasterised points
    @classmethod
    def create_horizontal_line(cls, stdscr, helpers, length, char):
        return cls(stdscr, helpers, np.stack([
            np.zeros(length, dtype="int64"),
            np.arange(length)
        ]).T, char)

    @classmethod
    def create_vertical_line(cls, stdscr, helpers, length, char):
        return cls(stdscr, helpers, np.stack([
            np.arange(length),
            np.zeros(length, dtype="int64")
        ]).T, char)


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.helpers = Helpers(stdscr)
        # self.ball = Ball(stdscr, self.center(np.array((1, 1))), np.array((1, 1)))
        self.ball = GameObject.create_point(stdscr, self.helpers, "O")
        self.ball.position = self.helpers.center(self.ball.size)
        self.ball.velocity = np.array((1, 1))
        self.left_paddle = GameObject.create_vertical_line(stdscr, self.helpers, 5, "X")
        self.left_paddle.position = np.array([5, 5])
        self.right_paddle = GameObject.create_vertical_line(stdscr, self.helpers, 5, "X")
        self.right_paddle.position = np.array([5, self.helpers.window_size[1] - 5])
        self.left_score = 0
        self.right_score = 0

    def update(self, key):
        # Check for collision between ball and top & bottom walls
        # If collision, then make ball "bounce" by negating its vertical velocity
        if self.ball.next_position[0] < 0 or self.ball.next_position[0] > self.helpers.window_max[0]:
            self.ball.velocity[0] *= -1

        # Check for collision between ball and left & right walls
        if self.ball.next_position[1] == 0:
            # Increment right score
            self.right_score += 1

            self.reset_ball()

        if self.ball.next_position[1] >= self.helpers.window_max[1]:
            # Increment left score
            self.left_score += 1

            self.reset_ball()

        # Check for collision between ball and paddles
        if self.ball.collides_with(self.left_paddle) or self.ball.collides_with(self.right_paddle):
            self.ball.velocity[1] *= -1

        # Move left paddle
        if key == ord("w"):
            self.left_paddle.velocity = np.array([-1, 0])
            if not self.left_paddle.is_within_window:
                self.left_paddle.velocity = np.array([0, 0])
        elif key == ord("s"):
            self.left_paddle.velocity = np.array([1, 0])
            if not self.left_paddle.is_within_window:
                self.left_paddle.velocity = np.array([0, 0])
        else:
            self.left_paddle.velocity = np.array([0, 0])

        # Move right paddle
        if key == curses.KEY_UP:
            self.right_paddle.velocity = np.array([-1, 0])
            if not self.right_paddle.is_within_window:
                self.right_paddle.velocity = np.array([0, 0])
        elif key == curses.KEY_DOWN:
            self.right_paddle.velocity = np.array([1, 0])
            if not self.right_paddle.is_within_window:
                self.right_paddle.velocity = np.array([0, 0])
        else:
            self.right_paddle.velocity = np.array([0, 0])

        # Update game objects
        self.ball.update()
        self.left_paddle.update()
        self.right_paddle.update()

    def draw(self):
        self.stdscr.clear()

        # Draw wall
        # todo: fix this (can't write to bottom-right corner)
        # for i in range(self.helpers.get_window_min[0], self.helpers.get_window_max[0] + 1):
        #     for j in range(self.helpers.get_window_min[1], self.helpers.get_window_max[1] + 1):
        #         if i == 0 or i >= self.helpers.get_window_max[0] or j == 0 or j >= self.helpers.get_window_max[1]:
        #             self.stdscr.getch()
        #             self.stdscr.addch(i, j, "X")
        # self.stdscr.box(0, 0)

        # Draw game objects
        self.ball.draw()
        self.left_paddle.draw()
        self.right_paddle.draw()

        # Draw score
        self.stdscr.addstr(0, 0, str(self.left_score))
        self.stdscr.addstr(0, self.helpers.right_align(len(str(self.right_score)))[1], str(self.right_score))

    def reset_ball(self):
        # Reset ball
        self.ball.position = self.helpers.center(self.ball.size)
        self.ball.velocity[1] *= -1

    def play(self):
        self.stdscr.timeout(50)

        self.draw()
        key = None
        # getch return value of 27 corresponds to escape key - doesn't look like curses has a constant for this
        while key != 27 and key != ord("q"):
            key = self.stdscr.getch()
            self.update(key)
            self.draw()

        self.stdscr.nodelay(False)


def main(stdscr):
    # TODO: Initialise colours

    # Show cursor
    curses.curs_set(1)

    # TODO: Title screen

    # Hide cursor
    curses.curs_set(0)

    game = Game(stdscr)
    game.play()

    # Show cursor
    curses.curs_set(1)

    # TODO: "Game over" screen


if __name__ == "__main__":
    curses.wrapper(main)
