from controller.ResizeHandler import ResizeHandler
from controller.StatsUpdate import StatsUpdater


class ThreadManager:
    def __init__(self, model, view, controller):
        self.model = model
        self.view = view
        self.controller = controller
        self.threads = []

    def start(self):
        self.threads = [
            ResizeHandler(self.view, self.model),
            StatsUpdater(self.model, self.view),
        ]
        for t in self.threads:
            t.start()

    def stop(self):
        self.model.running = False
        for t in self.threads:
            t.join(timeout=0.1)