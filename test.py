import requests
import lxml.html

import os
import argparse 
import atexit # keyboardinterrupt(Ctrl+C) 시 실행
from time import time
import signal 

bfs_li = list()
content = dict()

start_time = time()

def get_url(origin_url=None):
    
    if origin_url:
        bfs_li.append(origin_url)  

    while bfs_li:
        url = bfs_li.pop(0)

        try:
            req = requests.get(url) 
            root = lxml.html.fromstring(req.content)
        except:
            continue

        try: 
            subcategories = root.get_element_by_id('mw-subcategories')
            for a in subcategories.cssselect('a'):
                new_url = 'https://ko.wikipedia.org'+a.get('href')
                name = a.text_content()
                bfs_li.append(new_url)
                # print('sub',name)
        except:
            pass

        try:
            pages = root.get_element_by_id('mw-pages')
            for a in pages.cssselect('a'):
                new_url = 'https://ko.wikipedia.org'+a.get('href')
                name = a.text_content()
                content[name] = new_url
                # print(name)
        except:
            pass

def save():
    with open('can_url.lst','w') as f:
        f.write(('\n').join(bfs_li))
    with open('content.txt','a') as f:
        for key, value in content.items():
            f.write('{}   {} \n'.format(key, value))
    end_time = time()
    t = (end_time - start_time)//60
    print('save file... {} minute'.format(t))

def load():
    bfs_url_path = 'can_url.lst'
    if os.path.exists(bfs_url_path):
        with open('can_url.lst','r') as f:
            origin_url = [f.strip('\n') for f in f.readlines()]
        return origin_url
    else:
        open('can_url.lst','w')
        origin_li = list()
        return origin_li

# atexit.register(save) # Ctri+C 안먹히는 현상 발생

# 중간중간 저장하기 위한 장치 ('Ctrl+C')
def handler(signum, frame):
    print('   Add url to content.txt.... (url_number : {})'.format(url_i))
    save()

signal.signal(signal.SIGINT, handler)

if __name__=='__main__':
    start_time = time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--origin_url", default = 'https://ko.wikipedia.org/wiki/%EB%B6%84%EB%A5%98:%EC%88%98%ED%95%99')
    args = parser.parse_args()

    origin_li = load()
    bfs_li.extend(origin_li)

    if origin_li:
        start_url = None
    else:
        start_url = args.origin_url # '수학' 페이지 (분야의 가장 상위 페이지)

    get_url(start_url)
    save()