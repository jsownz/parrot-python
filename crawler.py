import requests, argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", dest="domain", help="Domain to crawl")
    parser.add_argument("-w", "--wordlist", dest="wordlist", help="wordlist to use")
    parser.add_argument("-p", "--path", dest="path", action="store_true", help="Set this flag to use path crawler on [-d] with [-w]")
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
if url[-1:] == "/":
    url = url[:-1]
    
with open(options.wordlist, "r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        if options.path:
            test_url = url + "/" + word
        else:
            test_url = word + "." + url
        response = request(test_url)
        if response:
            if options.path:
                print("[+] Discovered Path: " + test_url)
            else:
                print("[+] Discovered Subdomain: " + test_url)