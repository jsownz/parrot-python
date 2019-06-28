#!/usr/bin/env python

import scapy.all as scapy
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", help="Interface to sniff on")
    options = parser.parse_args()
    if not options.interface:
        # handle error
        parser.error("[-] Please specify an Interface to sniff on, use --help for more info")
    return options

def get_mac(ip_address):
    arp_request = scapy.ARP(pdst=ip_address)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]

    return answered_list[0][1].hwsrc

def sniff(interface):
    print("[+] Watching " + interface + " for ARP Spoofing..")
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def process_sniffed_packet(packet):
    if packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
        try:
            real_mac = get_mac(packet[scapy.ARP].psrc)
            response_mac = packet[scapy.ARP].hwsrc
            if real_mac != response_mac:
                print("[+]--- You are under an ARP Spoof Attack ---[+]")
        except IndexError:
            pass


options = get_arguments()
sniff(options.interface)