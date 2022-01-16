from typing import Tuple, Optional, Union, TextIO
from mitm import MITM, middleware, Connection, protocol, crypto
from network import send
from socket import socket
from threading import Thread

my_socket: Optional[socket] = None
file: Optional[TextIO] = None
mitm: Optional[MITM] = None


class FileLog(middleware.Middleware):
    @staticmethod
    async def mitm_started(host: str, port: int):
        file.write("MITM started on %s:%d.\n" % (host, port))
        print("MITM started on %s:%d.\n" % (host, port))

    @staticmethod
    async def client_connected(connection: Connection):
        host, port = connection.client.writer._transport.get_extra_info("peername")
        file.write("Client %s:%i has connected.\n" % (host, port))
        print("Client %s:%i has connected.\n" % (host, port))

    @staticmethod
    async def server_connected(connection: Connection):
        host, port = connection.server.writer._transport.get_extra_info("peername")
        file.write("Connected to server %s:%i.\n" % (host, port))
        print("Connected to server %s:%i.\n" % (host, port))

    @staticmethod
    async def client_data(connection: Connection, data: bytes) -> bytes:
        file.write("Client to server: \n\n\t%s\n" % data)
        print("Client to server: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def server_data(connection: Connection, data: bytes) -> bytes:
        file.write("Server to client: \n\n\t%s\n" % data)
        print("Server to client: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def client_disconnected(connection: Connection):
        file.write("Client has disconnected.\n")
        print("Client has disconnected.\n")

    @staticmethod
    async def server_disconnected(connection: Connection):
        file.write("Server has disconnected.")
        print("Server has disconnected.")


class NetLog(middleware.Middleware):
    @staticmethod
    async def mitm_started(host: str, port: int):
        send("MITM started on %s:%d." % (host, port), my_socket)

    @staticmethod
    async def client_connected(connection: Connection):
        host, port = connection.client.writer._transport.get_extra_info("peername")
        send("Client %s:%i has connected." % (host, port), my_socket)

    @staticmethod
    async def server_connected(connection: Connection):
        host, port = connection.server.writer._transport.get_extra_info("peername")
        send("Connected to server %s:%i." % (host, port), my_socket)

    @staticmethod
    async def client_data(connection: Connection, data: bytes) -> bytes:
        send("Client to server: \n\n\t%s\n" % data, my_socket)
        return data

    @staticmethod
    async def server_data(connection: Connection, data: bytes) -> bytes:
        send("Server to client: \n\n\t%s\n" % data, my_socket)
        return data

    @staticmethod
    async def client_disconnected(connection: Connection):
        send("Client has disconnected.", my_socket)

    @staticmethod
    async def server_disconnected(connection: Connection):
        send("Server has disconnected.", my_socket)


def filestart(path: str) -> bool:
    global file
    if file or my_socket:
        return False
    file = open(path, "wt")
    t = Thread(target=__start)
    t.start()
    return True


def netstart(address: Tuple[str, int]) -> bool:
    global my_socket
    if file or my_socket:
        return False
    my_socket = socket()
    my_socket.connect(address)
    t = Thread(target=__start)
    t.start()
    return True


def __start() -> bool:
    global mitm
    if my_socket and file:
        return False
    logger: Optional[type(middleware.Middleware)] = None
    if my_socket:
        logger = NetLog
    elif file:
        logger = FileLog
    else:
        return False

    mitm = MITM(middlewares=[logger], host="127.0.0.1",
    port=8888,
    protocols=[protocol.HTTP],
    buffer_size=8192,
    timeout=5,
    ssl_context=crypto.mitm_ssl_default_context(),)
    mitm.run()
    return True


def stop_sniffing() -> bool:
    global my_socket, file
    if not mitm:
        return False
    mitm.stop()
    if my_socket:
        my_socket.close()
    if file:
        file.close()
    my_socket = None
    file = None
    return True


