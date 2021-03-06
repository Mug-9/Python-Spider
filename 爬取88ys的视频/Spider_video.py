import spider_xici_free_proxy
import requests
from urllib.parse import unquote
import os
from bs4 import BeautifulSoup
import re
import time
import threading
import shutil

class Spider_Video(object):
    def __init__(self):
        self.url = input()
        self.url = self.video_url()
        self.header = spider_xici_free_proxy.getheader()
        self.proxy = spider_xici_free_proxy.random_free_proxy()
        self.sem = threading.Semaphore
        self.name = ""
        self.sem = threading.Semaphore(85)

    ## src loop_get
    def loop_get(self, url):
        loop = 50
        while loop:
            #print("loop: %s" % loop)
            try:
                requests.packages.urllib3.disable_warnings()
                response = requests.get(url, headers=self.header, proxies=self.proxy, verify=False, timeout=5)
                print(' 链接成功!!!')
                break
            except Exception as e:
                print(e)
                time.sleep(5)
                if loop == 0:
                    exit()
            loop -= 1
        return response

    #1 解析出m3u8列表&oplaylist
    def get_m3u8_list(self):
        response = self.loop_get(self.url).content.decode('utf-8')
        self.name = re.findall(r'mac_name=\'(.*?)\'', response)[0]
        m3u8_unescape = re.findall(r'mac_url=unescape\(\'(.*?)\'\);', response)[0]
        m3u8_encode = unquote(m3u8_unescape, encoding='utf-8')
        m3u8_list = re.findall(r'https://.*?.m3u8', m3u8_encode)
        header_name = m3u8_list[0].split('https')[len(m3u8_list[0].split('https'))-1].split('/')[2]
        m3u8_list = re.findall(r'https://%s.*?.m3u8' %header_name, m3u8_encode)
        return m3u8_list


    #2 获取每个的playlist的ts
    def get_ts(self, m3u8_url):
        response = self.loop_get(m3u8_url).content.decode('utf-8')
        is_m3u8 = re.findall(r'.*?.m3u8', response)
        if len(is_m3u8) != 0:
            m3u8_url = m3u8_url.replace("index.m3u8", is_m3u8[0])
            response = self.loop_get(m3u8_url).content.decode('utf-8')
        ts_list = re.findall(r'.*?.ts', response)
        new_ts_list=[]
        for ts in ts_list:
            new_ts_list.append(ts.split('/')[len(ts.split('/'))-1])
        ts_list = new_ts_list
        return ts_list,m3u8_url


    #3 多线程下载
    def download_thread(self, url, ts_list, name):
        path = "E://Video"
        if not os.path.exists(path):
            os.mkdir(path)
        path = "E://Video//%s" % self.name
        if not os.path.exists(path):
            os.mkdir(path)
        path = "%s//%s" % (path, name)
        if not os.path.exists(path):
            os.mkdir(path)
        for ts in ts_list:
            ts_url = url.replace("index.m3u8", ts)
            threading.Thread(target=self.download_method, args=(ts_url, path)).start()
            time.sleep(1)
        threading.Thread(target=self.Merge_ts, args=(path, len(ts_list), name)).start()


    #3.1 下载方法
    def download_method(self, url, path):
        with self.sem:
            name = url.split('/')[len(url.split('/'))-1]
            print("%s//%s开始下载" % (path, name))
            response = self.loop_get(url)
            with open("%s//%s" % (path, name), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            time.sleep(1)
            print("%s//%s下载完毕" % (path, name))


    #4 合并ts文件
    def Merge_ts(self, path, num, name):
        while True:
            os.chdir(path)
            print("%s文件数量 %s" % (path,len(os.listdir(path))))
            if len(os.listdir(path)) == num:
                os.system(r"copy /b *.ts %s.mp4" % name)
                print("%s合并完毕"%name)
                shutil.move("%s/%s.mp4" % (path, name), "%s.mp4" % path)
                os.chdir('E:/')
                shutil.rmtree(path)
                return
            else:
                time.sleep(1)


    #5 run
    def run(self):
        m3u8_list = self.get_m3u8_list()
        idx = 1
        for m3u8 in m3u8_list:
            ts_url = self.get_ts(m3u8)
            ts_list = ts_url[0] # 获取到第几集的ts_list
            m3u8 = ts_url[1]
            self.download_thread(m3u8, ts_list, "第%s集" % idx)
            idx += 1

    #6 得到视频url
    def video_url(self):
        video_id = self.url.split('/')[len(self.url.split('/'))-1][:-6]
        url = "https://www.88ys.com/vod-play-id-%s-src-1-num-1.html" % video_id
        return url


Spider_Video().run()
