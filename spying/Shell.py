import os
import subprocess


class Shell:
    def __init__(self):
        self.cwd = os.getcwd()
        self.live = True

    def terminate_command(self, command):
        if not self.live:
            return False
        command = command.strip()
        splited_command = command.split()
        output = ""
        if command.lower() == "exit":
            live = False
            return "GoodBye!"
        if splited_command[0].lower() == "cd":
            # cd command, change directory
            try:
                os.chdir(' '.join(splited_command[1:]))
                self.cwd = os.getcwd()
            except FileNotFoundError as e:
                # if there is an error, set as the output
                output = str(e)
        else:
            # execute the command and retrieve the results
            output = subprocess.getoutput(command)

        return f"{output}\n{self.cwd}"
