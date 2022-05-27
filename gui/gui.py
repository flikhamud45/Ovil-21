import threading

from turbo_flask import Turbo
import pathlib
from typing import Callable, List
from pathlib import Path
from flask import Flask, render_template, send_file, request, abort
import time

from consts import *
from network import check_ip
from network.client import Client

app = Flask(__name__)
turbo = Turbo(app)
# ovils: List[Client] = [Client("127.0.0.1"), Client("127.0.0.2"), Client("127.0.0.3"), Client("127.0.0.4"), Client("127.0.0.5"), Client("127.0.0.6"), Client("127.0.0.7")]
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
    ovil.connect_to_server()
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
    if result == "True":
        return "MITM started successfully"
    elif result == "False":
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
        return "This ovil is not connected"
    global dynamic_mitm_ovil
    if dynamic_mitm_ovil:
        return "Can't run 2 dynamic MITM simultaneously"
    i = ovils.index(ip)
    ovil = ovils[i]
    result = ovil.send_command("start_sniffing_on_net", [])
    if result == "True":
        dynamic_mitm_ovil = ovil
        return True
    elif result == "False":
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


def main():
    app.run(debug=False)


if __name__ == '__main__':
    main()
