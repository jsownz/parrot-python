import requests, argparse, re, urlparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", dest="domain", help="Domain to crawl")
    options = parser.parse_args()
    if not options.domain:
        # handle error
        parser.error("[-] Please specify a domain to crawl, use --help for more info")
    return options

def request(url):
    return requests.get(url)

def get_local_links(url):
    content = request(url).content
    return re.findall('(?:href=")(.*?)"', content)

def crawl(url):
    local_links = get_local_links(url)
    for link in local_links:
        link = urlparse.urljoin(url, link)

        if "#" in link:
            link = link.split("#")[0]

        if url in link and link not in target_links:
            target_links.append(link)
            crawl(link)

options = get_arguments()
if "http" not in options.domain:
        options.domain = "http://" + options.domain

target_links = []
crawl(options.domain)

for link in target_links:
    print(link)