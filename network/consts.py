
from enum import Enum

PORT = 8765
IP = "127.0.0.1"
ADDRESS = (IP, PORT)
MAX_SIZE_OF_MSG = 10  # the max length is 10 ^ this number
CHUNK_SIZE = 4  # the real size is 10 ^ this number
TIMEOUT_SOCKET = 5

class Massages(Enum):
    SEP = ', '
    EXIT = '0'
    BYE = "Good Bye"
    OK = "True"
    NOT_OK = "False"
    INVALID_COMMAND = "Invalid command"
    INVALID_NUMBER_OF_PARAMS = "Invalid number of params"
    INVALID_PARAMS = "invalid params"
    DEFAULT_PARAM = "D1E2F5AxU2LdTr"


MITM_DEFAULT_PORT = 8565
FILE_TRANSFER_PORT = 8956
UPLOAD_DEFAULT_PATH = "static\\uploads"
