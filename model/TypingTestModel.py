import time

from model.RandomTextGenerator import RandomTextGenerator


class TypingTestModel:
    def __init__(self, text="", language="it"):
        if text.strip() == "":
            self.text=RandomTextGenerator.generate_text(language=language, word_count=100)
            self.language = language
        else:
            self.text = text
            self.language = None
        self.user_input = ""
        self.start_time = None
        self.errors_counter = 0
        self.correct_chars = 0
        self.current_pos = 0
        self.has_error = False
        self.total_words = len(text.split())
        self.running = True


    def count_correct_chars(self):
        return sum(1 for i, c in enumerate(self.user_input) if i < len(self.text) and c == self.text[i])

    def calculate_progress(self):
        return int((self.correct_chars / len(self.text)) * 100) if len(self.text) > 0 else 0

    def calculate_wpm(self):
        if not self.start_time:
            return 0
        elapsed = (time.time() - self.start_time) / 60
        return int((self.correct_chars / 5) / elapsed) if elapsed > 0 else 0
    
    def calculate_accuracy(self):
        if len(self.text) == 0:
            return 100
        return int((len(self.text) / (len(self.text)+self.errors_counter)) * 100)