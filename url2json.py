import os
import json
import requests
import lxml.html
import hashlib
from tqdm import tqdm

json_data = {'latex_anno':[]}

def get_json(url):
    global count
    # 크롤링 불가능한 사이트는 skip
    json_format = {'latex':[]}
    try:
        req = requests.get(url) 
        root = lxml.html.fromstring(req.content)
    except:
        return

    root = lxml.html.fromstring(req.content)

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
    title = root.cssselect('h1')[0].text
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

def checklist(file_name=None, type=None):

    if type == 'check':
        with open('checklist.txt','r') as f:
            lst = [f.strip('\n') for f in f.readlines()]
            return lst

    else:
        with open('checklist.txt','a') as f:
            f.write('\n'+file_name)


if __name__=='__main__':

    lst = [file for file in os.listdir('./') if file.endswith('.lst')] # url 크롤링 데이터는 .lst로 저장됨
    done_lst = checklist(type='check')
    lst = set(lst)-set(done_lst)

    print('Total lst file list... {}'.format(lst))

    for i, url_path in enumerate(lst):

        json_data = {'latex_anno':[]}

        print('Start convert ... {}. {}'.format(i, url_path))
        with open(url_path, "r") as f:
            crawl_url = [url.strip('\n') for url in f.readlines()]

        for url in tqdm(crawl_url):
            get_json(url)   
        save_json()

        checklist(file_name = url_path)
        json_data = {'latex_anno':[]} # 초기화