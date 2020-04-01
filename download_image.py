# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
import requests
import re
from bs4 import BeautifulSoup as bs
import datetime

class DownloadImage():
    def __init__(self, max_dnum=1000, save_dir='~/Downloads/images_'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))):
        self.num = 0
        self.max_dnum = max_dnum
        self.list = []
        self.save_dir = os.path.expanduser(save_dir)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def recommend(self, url):
        Re = []
        try:
            html = requests.get(url)
        except error.HTTPError as e:
            return
        else:
            html.encoding = 'utf-8'
            bsObj = BeautifulSoup(html.text, 'html.parser')
            div = bsObj.find('div', id='topRS')
            if div is not None:
                listA = div.findAll('a')
                for i in listA:
                    if i is not None:
                        Re.append(i.get_text())
            return Re

    def find_images_info(self, url, maxpn=1000, perpn=60):
        logging.info('正在检测图片总数，请稍等.....')
        i = 0
        ulist = []
        while i < maxpn:
            Url = url + str(i)
            try:
                r = requests.get(Url, timeout=7)
            except Exception as e:
                i += perpn
                logging.info("Exception:{}".format(e))
                continue
            else:
                result = r.text
                pic_url = re.findall('"objURL":"(.*?)",', result, re.S)  # 先利用正则表达式找到图片url
                '''if len(pic_url) == 0:
                    break
                else:'''
                ulist.append(pic_url)
                i += perpn
        return ulist

    def download(self, url, keyword, maxpn=1000, perpn=60):
        i = 0
        while i < maxpn:
            try:
                rurl = url + str(i)
                r = requests.get(rurl, timeout=10)
            except error.HTTPError as e:
                logging.info("error.HTTPError:{}".format(e))
                logging.info('网络错误，请调整网络后重试')
                return
            else:
                html = r.text
                pic_url = re.findall('"objURL":"(.*?)",', html, re.S)
                logging.info('Finded :{} images, downloading soon...'.format(keyword))
                for each in pic_url:
                    if self.num >= self.max_dnum:
                        return
                    logging.info('正在下载第 {} 张图片，图片地址:{}'.format(str(self.num + 1), str(each)))
                    try:
                        if each is not None:
                            pic = requests.get(each, timeout=7)
                        else:
                            continue
                    except Exception as e:
                        logging.info('错误，当前图片无法下载, Exception:{}'.format(e))
                        continue
                    else:
                        string = os.path.join(self.save_dir, keyword + '_{}.jpg'.format(str(self.num)))
                        fp = open(string, 'wb')
                        fp.write(pic.content)
                        fp.close()
                        self.num += 1
            finally:
                i += perpn

def set_log(word):
    log_level = logging.INFO
    log_format = '%(asctime)s %(filename)s[%(lineno)d] %(levelname)s: %(message)s' # %(process)d
    log_datefmt = '%Y%m%d-%H%M%S'
    logging.basicConfig(level=log_level, format=log_format)
    formatter = logging.Formatter(fmt=log_format, datefmt=log_datefmt)
    lpath = "./logs"
    if not os.path.exists(lpath):
        os.makedirs(lpath)
    logname = os.path.join(lpath, 'images_{}.log'.format(word))
    loghandler = logging.handlers.RotatingFileHandler(logname, 'a',10*1024*1024, 500)
    loghandler.setLevel(log_level)
    loghandler.setFormatter(formatter)
    logging.getLogger('').addHandler(loghandler)

if __name__ == "__main__":
    word = '明星'# input("请输入搜索关键词(可以是人名，地名等): ")
    url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + word + '&pn='

    set_log(word)
    dli = DownloadImage(
        max_dnum=1000,
        save_dir='./downloads/images_{}_{}'.format(word, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        )
    # 1. 查找数量
    # uimages = dli.find_images_info(url, maxpn=1000, perpn=60)
    # logging.info('经过检测 {} 类图片共有 {} 张'.format(word, len(uimages)))
    # 2. 下载
    dli.download(url, keyword=word, maxpn=1000, perpn=60)
