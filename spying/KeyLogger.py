from typing import Callable

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

    def start(self, callback: Callable[[KeyboardEvent], None] | None = None) -> bool:
        callback = callback if callback else self.add
        if self.callback:
            return False
        self.callback = hook(callback)
        return True

    def stop(self) -> bool:
        if not self.callback:
            # raise RuntimeError("the keylogger is already stopped")
            return False
        unhook(self.callback)
        self.callback = None
        self.keys = Queue()
        return True
