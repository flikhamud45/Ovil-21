from typing import Tuple
from mitm import MITM, middleware
from network import send


my_socket = None
file = None


class FileLog(middleware.Middleware):
    @staticmethod
    async def mitm_started(host: str, port: int):
        logger.info("MITM started on %s:%d." % (host, port))

    @staticmethod
    async def client_connected(connection: Connection):
        host, port = connection.client.writer._transport.get_extra_info("peername")
        logger.info("Client %s:%i has connected." % (host, port))

    @staticmethod
    async def server_connected(connection: Connection):
        host, port = connection.server.writer._transport.get_extra_info("peername")
        logger.info("Connected to server %s:%i." % (host, port))

    @staticmethod
    async def client_data(connection: Connection, data: bytes) -> bytes:
        logger.info("Client to server: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def server_data(connection: Connection, data: bytes) -> bytes:
        logger.info("Server to client: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def client_disconnected(connection: Connection):
        logger.info("Client has disconnected.")

    @staticmethod
    async def server_disconnected(connection: Connection):
        logger.info("Server has disconnected.")


class NetLog(middleware.Middleware):
    @staticmethod
    async def mitm_started(host: str, port: int):
        logger.info("MITM started on %s:%d." % (host, port))

    @staticmethod
    async def client_connected(connection: Connection):
        host, port = connection.client.writer._transport.get_extra_info("peername")
        logger.info("Client %s:%i has connected." % (host, port))

    @staticmethod
    async def server_connected(connection: Connection):
        host, port = connection.server.writer._transport.get_extra_info("peername")
        logger.info("Connected to server %s:%i." % (host, port))

    @staticmethod
    async def client_data(connection: Connection, data: bytes) -> bytes:
        logger.info("Client to server: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def server_data(connection: Connection, data: bytes) -> bytes:
        logger.info("Server to client: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def client_disconnected(connection: Connection):
        logger.info("Client has disconnected.")

    @staticmethod
    async def server_disconnected(connection: Connection):
        logger.info("Server has disconnected.")



def start(address: Tuple[str, int]):

    mitm = MITM(middlewares=[Log])
    mitm.run()
