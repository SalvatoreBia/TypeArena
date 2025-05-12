import threading
import time


class StatsUpdater(threading.Thread):
    def __init__(self, model, view):
        super().__init__(daemon=True)
        self.model = model
        self.view = view

    def run(self):
        while self.model.running:
            self.model.correct_chars = self.model.count_correct_chars()
            self.view.update_stats()
            self.view.refresh_all()
            time.sleep(0.5)