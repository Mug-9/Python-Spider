import spider_cookies
import loopRequest
import time
import datetime
import re
from lxml import etree
import os
import threading
import requests

threadLock = threading.Lock()
cookie = {'__cfduid': 'dba3d14936dda3d552dc4684e12018a681618123786', 'XSRF-TOKEN': 'eyJpdiI6InRsY2hndjFtVElsYkthSGNQWHRCK2c9PSIsInZhbHVlIjoiZHlobWdcL3Fqb0VIRkpGU0diVVVIT3ZhVDhLZkpKVTBuTUp2elo3ajVqSDF1bFVjUzhkUmdORTZxdGR3ZEdIVWYiLCJtYWMiOiIwNzdhMGYzMTIyZTNkM2M2ZTM1YzliNzhjNTRmMDQ3ZTcyOTA4YjM3NjAzMzIwYmQwYmM5MDczMGVjODY3ZTQ3In0%3D', 'wallhaven_session': 'eyJpdiI6InA1TVFoaFZ0NGVnckZ3aWR3eDM4SGc9PSIsInZhbHVlIjoiNnZOb3FXemdmUEVGT0tEXC9paDhEXC9HM2liWTErZmdoV1hEUW00QVRBeU5CdndoTzBnR0JRQkY1aXdBUmNlUE5HIiwibWFjIjoiYzI2YWRkODY0ODA3MDBiZTA3MGY4ODQ1MmU5NWU5ZjAwZmViNWRhYWI3OGU0MWQ3Zjg2MmMzMTJiYjFlZDdkMyJ9', 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IlRpaWNsVGNzbitJUVc0a09jMVpNSXc9PSIsInZhbHVlIjoiaWZDM0lTVFBWaXk0MHFIXC9uS0UxcnpMVm12RWUyQVUwczFpY1pNMmdsa1lYSlZ4YzZpU0hOVFJ6XC8xc0ZxSFg4cThHd0hKV3dyeVVLeENHdjNmRU8rR0tLcGUzaU1Zam5hb211eUEwUGliUXZVeVlGVUo5TWN0dmU4ZFByUTFxcTZ0YXFjSWxiY0liTW55UWpPM1wvVHZVdDBrVWRGdVFqSVdUS1VveExTWW9hWWFIWnRSakpqRyswb2d1R01ZbzMzIiwibWFjIjoiZDgzMDRhZGM3ZTJkMWMyMTU5ZmIwNDgyM2YzZGViMTYwNGRjNGZiZDUzMjYyN2RmMjNkYjA0NjkxZDc4NGIxYiJ9'}

class SpiderWallPaper():
    def __init__(self):
        self.url = "https://wallhaven.cc/toplist?page="
       # self.cookies = spider_cookies.SpiderCookies()
        self.request = loopRequest.request
        self.sem = threading.Semaphore(100)
        self.download_log = open("download_log", "a+")
        self.error_log = open("error_log", "a+")
        self.count = 100

    # 1. 获取页面信息,获取每张战片所在页面的url
    def get_html(self, url):
        response = self.request.get(url, cookies=cookie)
        response_data = response.content.decode('utf-8')
        href_list = re.findall(r'<a class="preview" href="(.*?)"  target="_blank"  ></a>', response_data, re.S)
        return href_list

    # 2. 进入页面 获取图片的url
    def get_img_url(self, url):
        loop = 5
        img_url = []
        while loop:
            response = self.request.get(url)
            response_data = response.content.decode('utf-8')
            response_html = etree.HTML(response_data)
            img_url = response_html.xpath('//*[@id="wallpaper"]/@src')
            if len(img_url):
                return img_url
            loop -= 1
        self.error_log.write(url)
        print(url, "ERROR")
        return img_url

    # 4. 下载
    def img_download(self, html_url):
        with self.sem:
            thread_indent = threading.currentThread().ident
            url = self.get_img_url(html_url)[0]
            if len(url) == 0 or self.count <= 0:
                return
            print(url)
            img_name = url.split('/')[-1]
            if self.file_check(img_name):
                print("---%s 已存在" % img_name)
                return

            picture_mkdir = "E:\\picture"
            if not os.path.exists(picture_mkdir):
                os.mkdir(picture_mkdir)
            os.chdir(picture_mkdir)
            data_mkdir = "%s\\%s" % (picture_mkdir, datetime.date.today())
            if not os.path.exists(data_mkdir):
                os.mkdir(data_mkdir)
            os.chdir(data_mkdir)

            response = self.request.get(url)
            response_data = response.content
            print("---%s 开始写入" % img_name)
            threadLock.acquire()
            with open("%s" % img_name, "wb") as f:
                f.write(response_data)
            threadLock.release()
            print("---%s 写入完毕 -- count: %s" % (img_name, self.count))

            threadLock.acquire()
            self.download_log.write(img_name+'\n')
            self.count -= 1
            threadLock.release()


    # 5. 本地log
    def file_check(self, img_name):
        threadLock.acquire()
        self.download_log.seek(0, 0)
        file_content = self.download_log.read()
        threadLock.release()
        if img_name in file_content:
            return True
        else:
            return False

    # 6.run
    def run(self):
   #    loop = 50
   #    while loop:
   #        if self.cookies.Is:
   #            break
   #        else:
   #            self.cookies.update()
   #        time.sleep(2)
   #        loop -= 1
   #    if loop <= 0:
   #        self.error_log.write("Cookies 获得失败")
   #        return
        for i in range(1, 100):
            threads = []
            url = "%s%s" % (self.url, i)
            href_list = self.get_html(url)
            for html_url in href_list:
                m = threading.Thread(target=self.img_download, args=(html_url,))
                m.start()
                threads.append(m)
            for m in threads: 
                m.join()


if __name__ == '__main__':
    spiderWallpaper = SpiderWallPaper()
    spiderWallpaper.run()
