import curses
import textwrap


class TypingTestView:
    def __init__(self, stdscr, model):
        self.stdscr = stdscr
        self.model = model
        self.init_colors()
        self.init_window_sizes()
        self.create_windows()

    def init_colors(self):
        curses.curs_set(1)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, 8, -1)
        curses.init_pair(4, 15, -1)
        curses.init_pair(5, curses.COLOR_RED, -1)

    def init_window_sizes(self):
        self.max_y, self.max_x = self.stdscr.getmaxyx()
        self.top_height = max(int(self.max_y * 0.2), 5)
        self.bottom_height = max(self.max_y - self.top_height, 10)

    def create_windows(self):
        self.top_win = curses.newwin(self.top_height, self.max_x, 0, 0)
        self.bottom_win = curses.newwin(self.bottom_height, self.max_x, self.top_height, 0)
        self.refresh_all()

    def handle_resize(self):
        self.init_window_sizes()
        self.create_windows()
        self.display_content()

    def display_content(self):
        self.top_win.box()
        self.bottom_win.box()
        self.update_stats()
        self.update_instructions()
        self.display_text()
        self.refresh_all()

    def update_stats(self):
        self.top_win.addstr(3, 2, 
            f"WPM: {self.model.calculate_wpm()}   |   Progresso: {self.model.calculate_progress()}%   ",
            curses.color_pair(1))

    def update_instructions(self, message=None):
        self.top_win.addstr(1, 2, "Typing Test - Premi Esc per uscire", curses.color_pair(1))
        status = message or "Digita il testo che appare nella finestra sottostante        "
        self.top_win.addstr(2, 2, status, curses.color_pair(1 if not message else 5))

    def display_text(self):
        max_width = self.max_x - 6
        wrapped = self.wrap_text(max_width)
        
        for y, line in enumerate(wrapped, 3):
            for x, (i, char) in enumerate(line, 3):
                color = self.get_char_color(i)
                try:
                    self.bottom_win.addch(y, x, char, color)
                except curses.error:
                    pass

        self.position_cursor(wrapped)

    def wrap_text(self, width):
        wrapped = []
        index = 0
        for para in self.model.text.split('\n'):
            lines = textwrap.wrap(para, width, drop_whitespace=False)
            for line in lines:
                wrapped.append([(index + i, c) for i, c in enumerate(line)])
                index += len(line)
            index += 1  # Newline
        return wrapped

    def get_char_color(self, index):
        if index >= len(self.model.user_input):
            return curses.color_pair(3)
        if self.model.user_input[index] == self.model.text[index]:
            return curses.color_pair(4)
        return curses.color_pair(5)

    def position_cursor(self, wrapped):
        try:
            # Correzione della generazione delle coordinate
            y, x = next(
                (y_idx + 3, 3 + (self.model.current_pos - start))
                for y_idx, line in enumerate(wrapped)
                for start, _ in [line[0]]  # Estrae l'indice iniziale della riga
                if start <= self.model.current_pos < start + len(line)
            )
            self.bottom_win.move(y, x)
        except StopIteration:
            pass

    def refresh_all(self):
        self.top_win.noutrefresh()
        self.bottom_win.noutrefresh()
        curses.doupdate()