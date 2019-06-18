#!/usr/bin/env python

import scapy.all as scapy

def scan(ip_address):
    arp_request = scapy.ARP(pdst=ip_address)
    print(arp_request.summary())

scan("10.0.2.1/24")