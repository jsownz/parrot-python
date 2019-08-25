#!/usr/bin/env python

import argparse, requests

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", dest="list", help="file with list of ips to get info on")
    parser.add_argument("-ip", "--ip", dest="ip", help="IP to get info on")
    parser.add_argument("-o", "--outfile", dest="outfile", help="file to write to (otherwise prints to screen)")
    options = parser.parse_args()
    if not options.ip and not options.list:
        # handle error
        parser.error("[-] Must provide an IP or a list of IPs to get info on, use --help for more info")
    return options

def get_info(ip, options):
    ipinfo_url = "http://ipinfo.io/" + ip
    result = requests.get(ipinfo_url)
    if options.outfile:
        with open(options.outfile, "a") as final_file:
            final_file.write(result.text)
    else:
        print(result.text)


options = get_arguments()

if options.list:
    with open(options.list) as ip_file:
        for line in ip_file:
            get_info(line, options)
elif options.ip:
    get_info(options.ip, options)
