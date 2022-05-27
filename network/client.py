from typing import List
from queue import Queue
from threading import Thread
from consts import *
from . import *


class Client:
    def __init__(self, ip=IP):
        self.mitm_server_socket = None
        self.mitm_client_socket = None
        self.mitm_info = ["Dddd", "Ddd"]
        self.socket = socket()
        self.ip = ip
        self.connected = False

    def connect_to_server(self, ip: str = IP, port: int = PORT):
        self.ip = ip
        self.socket.connect((ip, port))
        self.connected = True

    def __eq__(self, other) -> bool:
        if isinstance(other, Client):
            return other.ip == self.ip
        return other == self.ip

    def disconnect(self):
        pass

    def send_command(self, command: str, params: List[str]):
        if command == "start_sniffing_on_net":
            send(command, self.socket)
            self.start_sniffing_on_net()
            response = receive_msg(self.socket)
            return response

        msg = [command]
        msg.extend(params)
        send(str(Massages.SEP).join(msg), self.socket)
        response = receive_msg(self.socket)
        return response

    def start_sniffing_on_net(self):
        self.mitm_server_socket = socket()
        self.mitm_server_socket.bind((self.ip, MITM_DEFAULT_PORT))
        self.mitm_server_socket.listen()
        self.mitm_client_socket, address = self.mitm_server_socket.accept()
        self.mitm_info = []
        t = Thread(target=self.mitm_thread)
        t.start()

    def mitm_thread(self):
        print("start to listen")
        try:
            while True:
                msg = receive_msg(self.mitm_client_socket)
                self.mitm_info.append(msg)
        except ConnectionError:
            return
