from socket import socket
from consts import *
import os


def check_ip(ip: str) -> bool:
    l = ip.split(".")
    if len(l) != 4:
        return False
    for n in l:
        try:
            n = int(n)
        except ValueError:
            return False
        if not 0 <= n <= 254:
            return False
    return True


def check_port(port: int) -> bool:
    try:
        port = int(port)
    except ValueError:
        return False
    return 1024 <= port <= 65535 # port 0 - 1023 are well know ports


def send(msg, client_socket: socket) -> None:
    """ sending a message to a client by sending the length of the message first
    :param msg: the message to send
    :param client_socket: the client to send the message
    """
    msg = msg.encode()
    if len(msg) >= 10 ** MAX_SIZE_OF_MSG: raise ValueError("The msg is too long")
    client_socket.send(str(len(msg)).zfill(MAX_SIZE_OF_MSG).encode())
    client_socket.send(msg)


def receive_msg(my_socket: socket) -> str:
    """receive a message from the server with a length of 999 max
    :param my_socket: the socket to get from
    :return: the message
    """
    try:
        data = my_socket.recv(MAX_SIZE_OF_MSG)
        length = int(data.decode())
        data = my_socket.recv(length)
        return data.decode(encoding="utf8")
    except UnicodeDecodeError:
        return ""


def binary_send(msg: str, client_socket: socket) -> str:
    """ sending a massage to a client by sending the length of the massage first without encoding the massage
    :param msg: the massage to send
    :param client_socket: the client to send the massage
    """
    client_socket.send(str(len(msg)).encode().zfill(CHUNK_SIZE))
    client_socket.send(msg)


def binary_receive(my_socket: socket) -> (int, bytes):
    """ recieve a bin from a client by sending the length first without encoding the massage
    :param my_socket: the client to send the massage
    :return: length, msg
    """
    length = int(my_socket.recv(CHUNK_SIZE).decode())
    # print(f"[*] Preparing to receive chunk of {length} bytes from server")
    chunk_data = my_socket.recv(length)
    # print(f"[*] Received {len(chunk_data)} bytes from server {file_size - given} remaining bytes")
    return length, chunk_data


def receive_file(my_socket: socket) -> (bool, str):
    """receive a file from
    return: whether succeeded and the path of the file
    """

    data = receive_msg(my_socket)
    if data.startswith("Error:"):
        print(data)
        return False, ""

    file_name, file_size = data.split()[0], int(data.split()[1])
    # print(f"[*] Preparing to receive {file_size} bytes from server")

    parent_directory = "\\".join(file_name.split("\\")[0:-1])
    if not os.path.exists(parent_directory):
        os.makedirs(parent_directory)
    with open(os.path.abspath(file_name), "wb") as file:
        given = 0
        error = False
        while not error and given < file_size:
            length, chunk_data = binary_receive(my_socket)
            assert length == len(chunk_data)
            try:
                if chunk_data.decode().startswith("Error:"):
                    error = True
                    # print(f"[!] Failed {chunk_data.decode()}")
            except ValueError:
                pass
            if not error:
                # print(f"[*] Writing to file {len(chunk_data)} bytes to {path}")
                file.write(chunk_data)
                given += length

    return not error, file_name


def send_file(path, client_socket) -> bool:
    """send a file to the client. if succeeded return success, else return error massage
    :param path: path of the file to send
    :param client_socket: the socket of the client to send to
    :return: return whether succeeded
    """
    try:

        size  = os.path.getsize(path)
        # print(f"[*] Sending the file size {size}")
        # send the length of the file to the client
        send(str(size), client_socket)
        with open(path, "rb") as file1:
            read = 0
            while read < size:
                # print(f"[*] Reading {MAX_LENGTH_OF_SEND} bytes from file {path}")
                massage = file1.read(MAX_LENGTH_OF_SEND)
                # print(f"[*] Read actually {len(massage)} bytes from file {path}")
                read += MAX_LENGTH_OF_SEND
                # print(f"[*] Sending {len(massage)} bytes to client")
                binary_send(massage, client_socket)
        # print(f"The file {path} has been sent")
    except Exception as e:
        # print(f"Couldn't send file because {e}")
        return False
    return True