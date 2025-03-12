class User:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.rows, self.cols = stdscr.getmaxyx()

    def resize_terminal(self):
        self.rows, self.cols = self.stdscr.getmaxyx()
