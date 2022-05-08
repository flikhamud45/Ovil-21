PROJECT_NAME = "Ovil-21"
ROOT_DIRECTORY = r"C:\Users\User\AppData\Local\Programs\Python\Python39\output"
ALTERNATE_ROOT_DIRECTORY = r"C:\Users\User\AppData\Local\Programs\Python\Python39\output\alt"
CERT_FOLDER = r"..\folder"
ROOT_CA_NAME = "root_ca"
DEFAULT_COMPUTER_NAME = "___Computer_name___"
START_UP_FOLDER = rf"C:\Users\{DEFAULT_COMPUTER_NAME}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
# TODO: replace computer name
SERVICE_NAME = "service"
SERVICE_PATH = r"C:\Users\User\AppData\Local\Programs\Python\Python39\output"
NSSM_PATH = f""
ALTERNATE_SERVICE_PATH = r"C:\Users\User\AppData\Local\Programs\Python\Python39\output\alt"
SERVICE_PATHS = [(f"{SERVICE_PATH}\\{SERVICE_NAME}1.exe", f"{ALTERNATE_SERVICE_PATH}\\{SERVICE_NAME}1.exe"), (f"{SERVICE_PATH}\\{SERVICE_NAME}2.exe", f"{ALTERNATE_SERVICE_PATH}\\{SERVICE_NAME}2.exe")]
PROTECTED_FILES = SERVICE_PATHS
PROTECTED_DIRS = [(ROOT_DIRECTORY, ALTERNATE_ROOT_DIRECTORY)]

# TODO: make nssm path and service path not the same