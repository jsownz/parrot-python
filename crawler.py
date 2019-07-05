import requests, argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", dest="domain", help="Domain to crawl")
    parser.add_argument("-w", "--wordlist", dest="wordlist", help="wordlist to use")
    options = parser.parse_args()
    if not options.domain:
        # handle error
        parser.error("[-] Please specify a domain to crawl, use --help for more info")
    if not options.wordlist:
        # handle error
        parser.error("[-] Please specify a wordlist to use, use --help for more info")
    return options

def request(url):
    if "http" not in url:
        url = "http://" + url
    try:
        return requests.get(url)
    except requests.exceptions.ConnectionError:
        pass

options = get_arguments()
url = options.domain

with open(options.wordlist, "r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        test_url = word + "." + url
        response = request(test_url)
        if response:
            print("[+] Discovered Subdomain: " + test_url)