#!/usr/bin/env python

import subprocess
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Which interface to change")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address to assign to interface")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        # handle error
        parser.error("[-] Please specify an interface, use --help for more info")
    if not options.new_mac:
        # handle error
        parser.error("[-] Please specify a MAC address, use --help for more info")
    return options

def change_mac(interface, new_mac):
    print("[+] Changing MAC address for " + interface + " to " + new_mac)

    subprocess.call(["ifconfig",interface,"down"])
    subprocess.call(["ifconfig","eth0","hw","ether",new_mac])
    subprocess.call(["ifconfig",interface,"up"])

options = get_arguments()
change_mac(options.interface, options.new_mac)