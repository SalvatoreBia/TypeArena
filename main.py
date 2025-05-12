import curses

from controller.TypingTestController import TypingTestController
from model.RandomTextGenerator import RandomTextGenerator


def main(stdscr):

    controller = TypingTestController(stdscr)
    controller.run()

if __name__ == "__main__":
    curses.wrapper(main)