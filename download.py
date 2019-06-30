#!/usr/bin/env python

import requests

def download(url):
    get_response = requests.get(url)
    # print(get_response.content)
    with open("sample.jpg", "wb") as outfile:
        outfile.write(get_response.content)

download("https://images.unsplash.com/photo-1561642193-7a507f4a87d8?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1000&q=80")