"""
Three classes where the constants used in the game are stored.
"""
class Colors:
    WHITE_BLACK = 0
    BLACK_WHITE = 256
    RED_BLACK = 512
    YELLOW_BLACK = 768
    YELLOW_RED = 1024
    WHITE_RED = 1280
    

class Keys:
    INTERACT = ord('x')
    QUIT = ord('q')

    def __init__(self, curses):
        self.KEY_DOWN = curses.KEY_DOWN
        self.KEY_UP = curses.KEY_UP
        self.KEY_RIGHT = curses.KEY_RIGHT
        self.KEY_LEFT = curses.KEY_LEFT
        self.RESIZE = curses.KEY_RESIZE


class Displacements:
    STEP_UP = (-6,0)
    STEP_DOWN = (6, 0)
    STEP_RIGHT = (0, 13)
    STEP_LEFT = (0, -13)
    ZERO = (0, 0)
