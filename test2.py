import os
import sys
import json
import signal 
import requests
import lxml.html
import hashlib
from tqdm import tqdm
import datetime as dt

import atexit # keyboardinterrupt(Ctrl+C) 시 실행

json_data = {'latex_anno':[]}
url_i = 0

def get_json(title, url):
    global count
    # 크롤링 불가능한 사이트는 skip
    json_format = {'latex':[]}
    try:
        req = requests.get(url) 
        root = lxml.html.fromstring(req.content)
    except:
        return

    # root = lxml.html.fromstring(req.content)

    # latex
    for img in root.cssselect('img'):
        latex = img.get('alt')
        if latex!=None and latex.startswith('{\displaystyle'):
            latex = latex.replace("\\displaystyle ","")
            latex = latex.replace("\\overline ","")
            latex = latex[1:-1]
            json_format['latex'].append(latex)
    if not json_format['latex']:
        return
    # id
    id = hashlib.sha1(url.encode('utf-8')).hexdigest()[:15]
    json_format['id'] = id
    # link
    json_format['link'] = url
    # title
    json_format['title'] = title
    # all_text
    # all_text = ''.join(root.itertext())
    # json_format['all_text'] = all_text
    json_data['latex_anno'].append(json_format)

def save_json():
    json_path = 'anno.json'

    if not os.path.isfile(json_path):
        with open(json_path, "w") as f:
            json.dump(json_data, f)
    else:
        with open(json_path, "r") as f:
            json_string = json.load(f)

        with open(json_path, "w") as f:
            json_string['latex_anno'] = json_string['latex_anno'] + json_data['latex_anno']
            json.dump(json_string, f)

def checklist(url_idx=None, check=False):
    global json_data

    if check == True:
        with open('checklist.txt','r') as f:
            lst = [f.strip('\n') for f in f.readlines()]
        l = lst[-1]
        date_time, url_idx = l.split('   ')
        print('Start from {}   {}...'.format(date_time, url_idx))
        return int(url_idx)

    else:
        save_json()
        json_data = {'latex_anno':[]}

        date_time = dt.datetime.now()
        date_time = str(date_time)[:-7]

        with open('checklist.txt','a') as f:
            f.write('\n{}   {}'.format(date_time, url_i))

# 중간중간 저장하기 위한 장치 ('Ctrl+C')
def handler(signum, frame):
    print('   Saveing anno.json .... (url_number : {})'.format(url_i))
    checklist(url_idx=url_i)
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

if __name__=='__main__':

    with open('content.txt','r') as f:
        lst = [f.strip('\n') for f in f.readlines()]

    url_idx = checklist(check=True)

    for i, l in enumerate(tqdm(lst[url_idx:])):
        url_i = url_idx + i
        title, url = l.split('   ')
        get_json(title, url)

    checklist(url_idx = url_i)