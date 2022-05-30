import subprocess
import tempfile
import winreg as reg
import os
from pathlib import Path
from spying.consts import START_UP_FOLDER


def create_shortcut(shortcut_path, target, arguments='', working_dir='') -> bool:
    shortcut_path = Path(shortcut_path)
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)

    def escape_path(path):
        return str(path).replace('\\', '/')

    def escape_str(str_):
        return str(str_).replace('\\', '\\\\').replace('"', '\\"')

    shortcut_path = escape_path(shortcut_path)
    target = escape_path(target)
    working_dir = escape_path(working_dir)
    arguments = escape_str(arguments)

    js_content = f'''
        var sh = WScript.CreateObject("WScript.Shell");
        var shortcut = sh.CreateShortcut("{shortcut_path}");
        shortcut.TargetPath = "{target}";
        shortcut.Arguments = "{arguments}";
        shortcut.WorkingDirectory = "{working_dir}";
        shortcut.Save();'''

    fd, path = tempfile.mkstemp('.js')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(js_content)
        subprocess.run([R'wscript.exe', path])
    finally:
        os.unlink(path)
    return True


def add_to_registry_startup(path: str) -> bool:
    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"

    # open the key to make changes to
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)

    # modify the opened key
    reg.SetValueEx(open, Path(path).name, 0, reg.REG_SZ, path)

    # now close the opened key
    reg.CloseKey(open)
    return True


def remove_from_startup_registry(name: str) -> bool:
    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = reg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"

    # open the key to make changes to
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)

    # modify the opened key
    reg.SetValueEx(open, name, 0, reg.REG_SZ, "")

    # now close the opened key
    reg.CloseKey(open)
    return True


def remove_from_startup_folder(name:str) -> bool:
    if not name.endswith(".lnk"):
        name += ".lnk"
    os.remove(str(Path(START_UP_FOLDER) / name))
    return True
