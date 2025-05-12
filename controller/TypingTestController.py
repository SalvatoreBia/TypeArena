
import locale
import curses
import time
from controller.ThreadManager import ThreadManager
from model.TypingTestModel import TypingTestModel
from model.RandomTextGenerator import RandomTextGenerator
from view.TypingTestView import TypingTestView


class TypingTestController:
    def __init__(self, stdscr, text="", language="it"):
        locale.setlocale(locale.LC_ALL, '')
        self.model = TypingTestModel(text, language)
        self.view = TypingTestView(stdscr, self.model)
        self.thread_manager = ThreadManager(self.model, self.view, self)
        self.stdscr = stdscr
        self.stdscr.timeout(100)
        self.stdscr.keypad(True)

    def handle_input(self, key):
        
        self.view.top_win.addstr(3, 50,
            f"key: {chr(key)} - {key}",
            curses.color_pair(1))
        self.view.top_win.refresh()
        if key == 27:  # ESC
            self.model.running = False
            exit(0)
        elif key == 18:  # Ctrl+R
            self.reset_game()
        elif key in (curses.KEY_BACKSPACE, 127, 8) and self.model.has_error: # Backspace
            self.handle_backspace()
        else:
            if not self.model.has_error:
                self.handle_character(key)
            else:
                self.model.errors_counter += 1

    def handle_backspace(self):
        if self.model.user_input:
            self.model.user_input = self.model.user_input[:-1]
            self.model.current_pos -= 1
            self.model.has_error = False
            self.view.update_instructions()

    def handle_character(self, key):
        if self.model.current_pos >= len(self.model.text):
            return

        char = chr(key)
        self.model.user_input += char
        self.model.current_pos += 1

        if not self.model.start_time:
            self.model.start_time = time.time()

        if char != self.model.text[self.model.current_pos - 1]:
            self.model.has_error = True
            self.model.errors_counter += 1
            self.view.update_instructions("Errore! Premi Backspace per correggere                ")

    def run(self):
        # Assicurati che il terminale sia in modalità wide-char
        curses.cbreak()
        curses.noecho()
        self.stdscr.keypad(True)
        self.thread_manager.start()

        try:
            while self.model.running:
                try:
                    key = self.stdscr.get_wch()
                except curses.error:
                    key = None

                if key is not None:
                    # Se key è str (es. 'à') ottieni il suo ord()
                    if isinstance(key, str):
                        code = ord(key)
                    else:
                        code = key
                    self.handle_input(code)

                self.view.display_content()

                if self.model.current_pos >= len(self.model.text) and not self.model.has_error:
                    self.model.running = False
                    self.show_final_stats()
                    # attendo ESC o Ctrl+R
                    while True:
                        try:
                            key = self.stdscr.get_wch()
                        except curses.error:
                            continue

                        if key == 18:   # Ctrl+R
                            self.reset_game()
                            break
                        elif key == 27: # ESC
                            return
        finally:
            self.thread_manager.stop()

    def reset_game(self):
        if(self.model.language == None):
            self.model.__init__(self.model.text)
        else:
            self.model.__init__(language=self.model.language)
        self.view.create_windows()
    def show_final_stats(self):
        final_wpm = self.model.calculate_wpm()
        accuracy = self.model.calculate_accuracy()
        self.view.top_win.addstr(3, 2,
            f"Test completato! WPM finale: {final_wpm}   Accuratezza: {accuracy}%   ",
            curses.color_pair(1))
        self.view.refresh_all()
        