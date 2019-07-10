#!/usr/bin/env python

import requests
import re
import urlparse
from BeautifulSoup import BeautifulSoup

class Scanner:
    def __init__(self, url, ignore_links):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []
        self.links_to_ignore = ignore_links
        self.vulns_found = 0

    def get_local_links(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content)

    def crawl(self, url=None):
        if url == None:
            url = self.target_url
        local_links = self.get_local_links(url)
        for link in local_links:
            link = urlparse.urljoin(url, link)

            if "#" in link:
                link = link.split("#")[0]

            if self.target_url in link and link not in self.target_links:
                for ignore_link in self.links_to_ignore:
                    if ignore_link in link:
                        pass
                self.target_links.append(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content)
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        form_action = form.get("action")
        form_action = urlparse.urljoin(url, form_action)
        form_method = form.get("method")
        form_inputs = form.findAll("input")
        post_data = {}
        for input in form_inputs:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
        if form_method == "post":
            return self.session.post(form_action, data=post_data)
        return self.session.get(form_action, params=post_data)

    def run_scanner(self):
        print("[+] " + str(len(self.target_links)) + " links Found.")
        print("[+] Running tests...\n\n")
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                xss_vulnerable = self.test_xss_in_form(form, link)
                if xss_vulnerable:
                    print("[+] XSS Vulnerability found! - " + link)
                    self.vulns_found += 1
            if "=" in link:
                xss_vulnerable = self.test_xss_in_url(link)
                if xss_vulnerable:
                    print("[+] XSS Vulnerability found! - " + link)
                    self.vulns_found += 1
        
        if self.vulns_found > 0:
            print("\n\n[+] " + str(self.vulns_found) + " Vulnerabilities Found!")
        else:
            print("\n\n[-] No Vulnerabilities Found.")

    def test_xss_in_form(self, form, url):
        xss_test_script = "<sCript>alert(1)</scriPt>"
        response = self.submit_form(form, xss_test_script, url)
        return xss_test_script in response.content

    def test_xss_in_url(self, url):
        xss_test_script = "<sCript>alert(1)</scriPt>"
        response = self.session.get(url.replace("=", "=" + xss_test_script))
        return xss_test_script in response.content
