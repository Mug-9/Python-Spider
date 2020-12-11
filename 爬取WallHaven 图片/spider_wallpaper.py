import spider_cookies
import loopRequest
import time
import datetime
import re
from lxml import etree
import os
import threading

threadLock = threading.Lock()


class SpiderWallPaper():
    def __init__(self):
        self.url = "https://wallhaven.cc/toplist?page="
        self.cookies = spider_cookies.SpiderCookies()
        self.request = loopRequest.request
        self.sem = threading.Semaphore(100)
        self.download_log = open("download_log", "a+")
        self.error_log = open("error_log", "a+")
        self.count = 100

    # 1. 获取页面信息,获取每张战片所在页面的url
    def get_html(self, url):
        response = self.request.get(url, cookies=self.cookies.cookies)
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
    def img_download(self, url):
        with self.sem:
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
        loop = 50
        while loop:
            if self.cookies.Is:
                break
            else:
                self.cookies.update()
            time.sleep(2)
            loop -= 1
        if loop <= 0:
            self.error_log.write("Cookies 获得失败")
            return
        for i in range(2, 100):
            url = "%s%s" % (self.url, i)
            href_list = self.get_html(url)
            for html_url in href_list:
                img_url = self.get_img_url(html_url)
                if len(img_url) and self.count > 0:
                    threading.Thread(target=self.img_download, args=(img_url[0],)).start()


if __name__ == '__main__':
    spiderWallpaper = SpiderWallPaper()
    spiderWallpaper.run()