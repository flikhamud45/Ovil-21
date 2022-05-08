import pathlib
import os
import shutil
from functools import reduce
from typing import Tuple, List
# import win32serviceutil
# import win32service
# import win32event
# import servicemanager
# import socket
import subprocess
import pathlib
# import time
# import sys
# from SMWinservice import SMWinservice
# import random
import time
from consts import *

# live = True
# num = 2


def install_ovil():
    # TODO: finnish this
    pass


def secure_files(protected_files: List[Tuple[str, str]] = SERVICE_PATHS, protected_dirs: List[Tuple[str, str]] = PROTECTED_DIRS) -> None:
    for service in protected_files:
        p1 = pathlib.Path(service[0])
        p1.parent.mkdir(parents=True, exist_ok=True)
        p2 = pathlib.Path(service[1])
        p2.parent.mkdir(parents=True, exist_ok=True)
        if not p1.exists():
            shutil.copyfile(p2, p1)
        if not p2.exists():
            shutil.copyfile(p1, p2)

    for d in protected_dirs:
        og_dir = pathlib.Path(d[0])
        alt_dir = pathlib.Path(d[0])
        for file in og_dir:
            # TODO: finnish going through dirs


def run(command: str) -> Tuple[str, str]:
    result = subprocess.run(command.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return result.stdout.decode()[::2].strip(), result.stderr.decode()[::2].strip()


def infinite_service(service_name: str) -> None:
    install_service(service_name, f"{SERVICE_PATH}\\{service_name}.exe", f"{ROOT_DIRECTORY}\\{'nssm.exe'}",
                    override=False)
    while True:
        try:
            # time.sleep(1)
            secure_files()
            install_ovil()
            install_service(service_name, f"{SERVICE_PATH}\\{service_name}.exe", f"{ROOT_DIRECTORY}\\{'nssm.exe'}")
        except:
            pass


def check_status(service_name: str, nssm_path: str = "nssm.exe") -> Tuple[str, str]:
    return run(f"{nssm_path} status {service_name}")


def is_started(service_name: str, nssm_path: str = "nssm.exe") -> bool:
    return check_status(service_name, nssm_path)[0] == "SERVICE_RUNNING"


def is_installed(service_name: str, nssm_path: str = "nssm.exe") -> bool:
    status, err = check_status(service_name, nssm_path)
    return not err.startswith("Can't open service!") and \
           (status == "SERVICE_RUNNING" or status == "SERVICE_STOPPED" or status == "SERVICE_PAUSED")


def start_service(service_name: str, nssm_path: str = "nssm.exe") -> Tuple[str, str]:
    return run(f"{nssm_path} start {service_name}")


def remove_service(service_name: str, nssm_path: str = "nssm.exe") -> tuple[tuple[str, str], Tuple[str, str]]:
    r1 = run(f"{nssm_path} stop {service_name}")
    r2 = run(f"{nssm_path} remove {service_name} confirm")
    return r1, r2


def install_service(service_name: str, service_path: str, nssm_path: str = "nssm.exe", start: bool = True,
                    override: bool = False, directory_path=None) -> None:
    if not is_installed(service_name, nssm_path):
        print(run(f"{nssm_path} install {service_name} {service_path}"))
        if directory_path:
            print(run(f"{nssm_path} set {service_name} AppDirectory {directory_path}"))
    elif override:
        print(remove_service(service_name, nssm_path))
        install_service(service_name, service_path, nssm_path, False, False, directory_path)
    if start and not is_started(service_name, nssm_path):
        print(start_service(service_name, nssm_path))


# class Service(win32serviceutil.ServiceFramework):
#     _svc_name_ = f"Ovil-21_{num}"
#     _svc_display_name_ = f"Ovil-21_{num}"
#
#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#         socket.setdefaulttimeout(60)
#         self.live = False
#
#     def SvcStop(self):
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)
#         global num
#         self.live = False
#         num += 1
#         start_service()
#
#     def SvcDoRun(self):
#         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
#                               (self._svc_name_, ''))
#         self.live = True
#         self.main()
#
#     def main(self):
#         f = open(r"c:\what.txt", "wt")
#         f.write(f"writen by {self._svc_name_}:\n")
#         n = 0
#         # while self.live:
#         #     f.write(f"{n}\n")
#         f.close()
#
def remove_services(services: List[str], nssm_path: str) -> None:
    services_live = True
    while services_live:
        for service in services:
            print(remove_service(service, nssm_path))
        services_live = False
        for service in services:
            if is_installed(service, nssm_path):
                services_live = True


if __name__ == "__main__":
    while True:
        secure_files()
    # remove_services([f"{SERVICE_NAME}1", f"{SERVICE_NAME}2"], f"{ROOT_DIRECTORY}\\{'nssm.exe'}")
    # install_service(f"{SERVICE_NAME}1", SERVICE_PATHS[0][0], f"{ROOT_DIRECTORY}\\{'nssm.exe'}",
    #                 override=True)
    # install_service(f"{SERVICE_NAME}2", SERVICE_PATHS[1][0], f"{ROOT_DIRECTORY}\\{'nssm.exe'}",
    #                 override=True)
