import multiprocessing
import threading
import winreg
from typing import Tuple

import spying.snnifing
from spying.snnifing import __filestart, __netstart, my_socket, file, mitm, set_reg

p: multiprocessing.Process | None = None


def filestart(path: str, address: Tuple[str, int]):
    global p
    p = multiprocessing.Process(target=__filestart, args=(path, address))
    p.start()
    p.join()


def netstart(address: Tuple[str, int]):
    global p
    p = multiprocessing.Process(target=__netstart, args=(address, ))
    p.start()
    p.join()


def stop_sniffing() -> bool:
    if spying.snnifing.my_socket or spying.snnifing.file:
        if not mitm:
            return False
        mitm.stop()
        if spying.snnifing.my_socket:
            spying.snnifing.my_socket.close()
        if spying.snnifing.file:
            spying.snnifing.file.close()
        my_socket = None
        file = None
    else:
        global p
        p.terminate()
    # os.system('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0')
    # sys.stdout.write("yes")
    set_reg("ProxyEnable", 0, winreg.REG_DWORD)
    return True


def is_MITM_runs():
    return p and p.is_alive()


def main():
    t = threading.Thread(target=filestart, args=("logger.txt", ("127.0.0.1", 4)))
    t.start()
    # filestart("logger.txt", ("127.0.0.1", 4))
    # print("started")
    # input()
    # # time.sleep(3)
    # stop_sniffing()
    # # print("stopped")


if __name__ == "__main__":
    main()
    print("finished")
