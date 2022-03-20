#!/usr/bin/env python3

import scapy.all as scapy
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="IP Range to scan (10.0.2.1/24)")
    options = parser.parse_args()
    if not options.target:
        # handle error
        parser.error("[-] Please specify an IP range to scan, use --help for more info")
    return options

def scan(ip_address):
    arp_request = scapy.ARP(pdst=ip_address)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]

    clients_list = []
    for answer in answered_list:
        client = {"ip": answer[1].psrc, "mac": answer[1].hwsrc}
        clients_list.append(client)
    return clients_list

def print_results(results_list):
    print("\nIP\t\t\tMAC Address")
    for client in results_list:
        print(client["ip"] + "\t\t" + client["mac"])

options = get_arguments()
results_list = scan(options.target)
print_results(results_list)
