from socket import socket
from network.consts import *
import os
from pathlib import Path


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


def send(msg: str, client_socket: socket) -> None:
    """ sending a message to a client by sending the length of the message first
    :param msg: the message to send
    :param client_socket: the client to send the message
    """
    msg = msg.encode()
    if len(msg) >= 10 ** MAX_SIZE_OF_MSG: raise ValueError("The msg is too long")
    client_socket.sendall(str(len(msg)).zfill(MAX_SIZE_OF_MSG).encode())
    client_socket.sendall(msg)
    print(f"sent {msg}")


def receive_msg(my_socket: socket) -> str:
    """receive a message from the server with a length of 999 max
    :param my_socket: the socket to get from
    :return: the message
    """
    try:
        data = my_socket.recv(MAX_SIZE_OF_MSG)
        length = int(data.decode())
        data = b""
        while len(data) < length:
            data += my_socket.recv(length - len(data))
        data = data.decode(encoding="utf8")
        print(f"recieved {data}")
        return data
    except UnicodeDecodeError:
        return ""


def binary_send(msg: bytes, client_socket: socket):
    """ sending a massage to a client by sending the length of the massage first without encoding the massage
    :param msg: the massage to send
    :param client_socket: the client to send the massage
    """
    client_socket.sendall(str(len(msg)).encode().zfill(CHUNK_SIZE))
    client_socket.sendall(msg)


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
    if data.startswith(":Error:") or data in [m.value for m in Massages]:
        print(data)
        return False, data

    file_name, file_size = " ".join(data.split()[0:-1]), int(data.split()[-1])
    # print(f"[*] Preparing to receive {file_size} bytes from server")
    path = Path(UPLOAD_DEFAULT_PATH) / Path(file_name).name
    with open(path, "wb") as file:
        given = 0
        error = False
        while not error and given < file_size:
            length, chunk_data = binary_receive(my_socket)
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

    return not error, str(path)


def send_file(path, client_socket) -> str | bool:
    """send a file to the client. if succeeded return success, else return error massage
    :param path: path of the file to send
    :param client_socket: the socket of the client to send to
    :return: return whether succeeded
    """
    try:
        if Path(path).is_dir():
            return ":Error: Can't steal directories"
        if not Path(path).is_file():
            return f":Error: There is not file named {path}"

        size = os.path.getsize(path)
        # print(f"[*] Sending the file size {size}")
        # send the length of the file to the client
        send(f"{path} {size}", client_socket)
        with open(path, "rb") as file1:
            read = 0
            while read < size:
                # print(f"[*] Reading {MAX_LENGTH_OF_SEND} bytes from file {path}")
                massage = file1.read(10**CHUNK_SIZE-1)
                # print(f"[*] Read actually {len(massage)} bytes from file {path}")
                read += 10**CHUNK_SIZE-1
                # print(f"[*] Sending {len(massage)} bytes to client")
                binary_send(massage, client_socket)
        # print(f"The file {path} has been sent")
    except Exception as e:
        # print(f"Couldn't send file because {e}")
        return ":Error: " + str(e)
    return True
