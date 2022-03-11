import socket
from consts import *
from . import *


class Client:
    def __init__(self):
        self.socket = socket.socket()

    def connect_to_server(self, address=ADDRESS):
        self.socket.connect(address)

