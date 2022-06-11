import ctypes
import sys


def is_admin():
    """checks whther tou are an admin

    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def make_admin():
    """
    If tou are not admin make you admin and return False, otherwise return True
    """
    if is_admin():
        print("The program has admin rights")
        return True
    else:
        print("Re-run the program with admin rights")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False
