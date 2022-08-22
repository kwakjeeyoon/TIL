import requests
import lxml.html

import os
import argparse

url_li = set()

def get_url(url, count):
    # origin_url에 해당하는 하위 url 크롤링
    if count == 0:
        return 
    # 크롤링 불가능한 사이트는 skip
    try:
        req = requests.get(url) 
        root = lxml.html.fromstring(req.content)
    except:
        return

    root = lxml.html.fromstring(req.content)
    for a in root.cssselect('a'):
        new_url = a.get('href')
        title = a.get('title')
        if new_url!=None and title != None and new_url.startswith('/wiki/'):
            new_url = 'https://ko.wikipedia.org'+new_url
            url_li.add(new_url)
            get_url(new_url, count - 1)

def save_url():

    url_path = 'url.lst'

    if not os.path.isfile(url_path):
        open(url_path, 'w')

    with open(url_path, "r") as f:
        origin_url = [url.strip('\n') for url in f.readlines()]
        origin_url = set(origin_url)
        origin_url.update(url_li) # 기존 크롤링 url과 새로운 url 병합

    with open(url_path, "w") as f:
        f.write(origin_url.join('\n'))

    print('Save {} url!'.format(len(url_li)))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--origin_url")
    parser.add_argument("-d","--depth", default = 2)
    args = parser.parse_args()

    get_url(args.origin_url, args.depth)
    save_url()
