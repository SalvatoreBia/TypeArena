import threading
import time


class ResizeHandler(threading.Thread):
    def __init__(self, view, model):
        super().__init__(daemon=True)
        self.view = view
        self.model = model
        self.last_size = (0, 0)

    def run(self):
        while self.model.running:
            current_size = (self.view.max_y, self.view.max_x)
            if current_size != self.last_size:
                self.view.handle_resize()
                self.last_size = current_size
            time.sleep(0.2)