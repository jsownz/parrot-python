#!/usr/bin/env python

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.set_headless()

assert opts.headless

#browser = Firefox(options=opts)

def crawl(url):
  browser = Firefox(options=opts)
  browser.get(url)
  local_links = browser.find_elements_by_tag_name("a")

  print("Crawling " + url + " " + str(len(local_links)) + " links")

  for link in local_links:
    link = link.get_attribute('href')
#    print("[+]" + link)
    if main_url in link and "mailto" not in link and link not in target_links:
      target_links.append(link)
      crawl(link)
  browser.close()


target_links = []
main_url = "https://www.frozensoliddesigns.com"
crawl(main_url)

for link in target_links:
  print(link)
