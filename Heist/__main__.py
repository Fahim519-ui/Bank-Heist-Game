"""
The main function of the game.
"""
import curses
from heist import constants
from heist.user import User
from heist import maps

def main(stdscr):
    #Terminal initialisation
    stdscr.clear()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_RED)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)

    #Start game
    title_screen = maps.Title(curses, User(stdscr), constants.Keys(curses))
    title_screen.play()


if __name__ == "__main__":
    curses.wrapper(main)
