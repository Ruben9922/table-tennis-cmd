import curses
import numpy as np
import game_utilities as gu


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.ball = gu.GameObject.create_point(stdscr, "O")
        self.ball.position = gu.center(stdscr, self.ball.shape.size)
        self.ball.velocity = np.array((1, 1))
        self.left_paddle = gu.GameObject.create_vertical_line(stdscr, 5, "X")
        self.left_paddle.position = np.array([5, 5])
        self.right_paddle = gu.GameObject.create_vertical_line(stdscr, 5, "X")
        self.right_paddle.position = np.array([5, gu.window_size(stdscr)[1] - 5])
        self.left_score = 0
        self.right_score = 0

    def update(self, key):
        # Check for collision between ball and top & bottom walls
        # If collision, then make ball "bounce" by negating its vertical velocity
        if self.ball.next_position[0] < 0 or self.ball.next_position[0] > gu.window_max(self.stdscr)[0]:
            self.ball.velocity[0] *= -1

        # Check for collision between ball and left & right walls
        if self.ball.next_position[1] == 0:
            # Increment right score
            self.right_score += 1

            self.reset_ball()

        if self.ball.next_position[1] >= gu.window_max(self.stdscr)[1]:
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
        gu.addstr_multiline_aligned(self.stdscr, [str(self.left_score)], gu.HorizontalAlignment.LEFT, gu.VerticalAlignment.TOP)
        gu.addstr_multiline_aligned(self.stdscr, [str(self.right_score)], gu.HorizontalAlignment.RIGHT, gu.VerticalAlignment.TOP)

    def reset_ball(self):
        # Reset ball
        self.ball.position = gu.align(self.stdscr, self.ball.shape.size, gu.HorizontalAlignment.CENTER, gu.VerticalAlignment.CENTER)
        self.ball.velocity[1] *= -1

    # def show_point_screen(self):
        # todo: finish this
        # self.stdscr.timeout(2000)
        # self.stdscr.addstr(self.)
        # self.stdscr.getch()

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
