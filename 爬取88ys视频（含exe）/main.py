from tkinter import *
import spider_xici_free_proxy
import requests
from tkinter import *
import tkinter.font as tf
from urllib.parse import unquote
import os
import re
import time
import threading
import shutil
import signal


class GUI():
    def __init__(self, master):
        self.parent = master
        self.url_text = ""
        self.parent.title('Spider_Video')
        self.frame_top = Frame(self.parent)
        self.frame_down = Frame(self.parent)
        self.label1 = Label(self.frame_top, text=' U  R  L ')
        self.url_input = Entry(self.frame_top, width=100)
        self.btn_accept = Button(self.frame_top, text="  确  定  ", command=lambda: self.btn_click_accept())
        self.btn_cancel = Button(self.frame_top, text = "  取  消  ", command=self.btn_click_stop)
        self.download_text = Text(self.frame_down)
        self.url_ck = False
        self.view_run()

    def view_run(self):
        self.label1.pack(side=LEFT)
        self.url_input.place(relx=0.1, relheight=1)
        self.btn_cancel.pack(side=RIGHT)
        self.btn_accept.pack(side=RIGHT)
        self.download_text.pack(fill=X)
        self.frame_top.pack(fill=X)
        self.frame_down.pack(fill=X)
        self.download_text.tag_add('Accept', END)
        self.download_text.tag_config('Accept', font=ft, foreground='green', background='black')
        self.download_text.tag_add('Wait', END)
        self.download_text.tag_config('Wait', font=ft, foreground='yellow', background='black')
        self.download_text.tag_add('Wrong', END)
        self.download_text.tag_config('Wrong', font=ft, foreground='red', background='black')
        self.url_input.configure(font="JetBrains 14 bold")

    def btn_click_accept(self):
        url = self.url_input.get()
        if len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)):
            self.url_text = url
            self.download_text.insert(END,  "链接为: %s\n" % self.url_text, 'Accept')
            self.download_text.see(END)
            self.url_ck = True
        else:
            self.download_text.insert(END, "链接错误,请重新输入\n", 'Wrong')
            self.download_text.see(END)
            self.url_ck = False

    def btn_click_stop(self):
        os.kill(os.getpid(), signal.SIGINT)

class Spider_Video():
    def __init__(self, master):
        self.parent = master
        self.gui = GUI(self.parent)
        self.url = ""
        self.header = spider_xici_free_proxy.getheader()
        self.proxy = spider_xici_free_proxy.random_free_proxy()
        self.sem = threading.Semaphore
        self.name = ""
        self.sem = threading.Semaphore(150)
        self.play_list = True

    def wait_begin(self):
        while TRUE:
            if self.gui.url_ck:
                self.run()
                return
            time.sleep(1)

    # src loop_get
    def loop_get(self, url):
        loop = 50
        while loop:
            try:
                requests.packages.urllib3.disable_warnings()
                response = requests.get(url, headers=self.header, proxies=self.proxy, verify=False, timeout=5)
                self.gui.download_text.insert(END, ' 链接成功!!!\n', 'Accept')
                self.gui.download_text.see(END)
                break
            except Exception as e:
                self.gui.download_text.insert(END, "%s\n" % e, 'Wrong')
                self.gui.download_text.see(END)
                time.sleep(5)
                if loop == 0:
                    exit()
            loop -= 1
        return response

    # 1 解析出m3u8列表&oplaylist
    def get_m3u8_list(self):
        response = self.loop_get(self.url).content.decode('utf-8')
        self.name = re.findall(r'mac_name=\'(.*?)\'', response)[0]
        m3u8_unescape = re.findall(r'mac_url=unescape\(\'(.*?)\'\);', response)[0]
        m3u8_encode = unquote(m3u8_unescape, encoding='utf-8')
        sourcelist = m3u8_encode.split("$$$")
        print(sourcelist)
        m3u8_list = []
        for source in sourcelist:
            m3u8_list = re.findall(r'https://.*?.m3u8', source)
            if len(m3u8_list):
                return m3u8_list

    # 2 获取每个的playlist的ts
    def get_ts(self, m3u8_url):
        response = self.loop_get(m3u8_url).content.decode('utf-8')
        is_m3u8 = re.findall(r'.*?.m3u8', response)
        if len(is_m3u8) != 0:
            m3u8_url = m3u8_url.replace("index.m3u8", is_m3u8[0])
            response = self.loop_get(m3u8_url).content.decode('utf-8')
        ts_list = re.findall(r'.*?.ts', response)
        new_ts_list = []
        if len(is_m3u8) != 0:
            for ts in ts_list:
                new_ts_list.append(ts.split('/')[len(ts.split('/')) - 1])
            ts_list = new_ts_list
        return ts_list, m3u8_url

    # 3 多线程下载
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
            ts_url = url.replace(url.split('/')[len(url.split('/'))-1], ts.split('/')[len(ts.split('/'))-1])
            threading.Thread(target=self.download_method, args=(ts_url, path)).start()
            time.sleep(1)
        threading.Thread(target=self.merge_ts, args=(path, len(ts_list), name)).start()

    # 3.1 下载方法
    def download_method(self, url, path):
        with self.sem:
            name = url.split('/')[len(url.split('/')) - 1]
            self.gui.download_text.insert(END, "%s//%s开始下载\n" % (path, name), 'Wait')
            self.gui.download_text.see(END)
            response = self.loop_get(url)
            with open("%s//%s" % (path, name), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            time.sleep(1)
            self.gui.download_text.insert(END, "%s//%s下载完毕\n" % (path, name), 'Accept')
            self.gui.download_text.see(END)

    # 4 合并ts文件
    def merge_ts(self, path, num, name):
        while True:
            os.chdir(path)
            self.gui.download_text.insert(END, "%s文件数量 %s\n" % (path, len(os.listdir(path))), 'Wait')
            self.gui.download_text.see(END)
            if len(os.listdir(path)) == num:
                os.system(r"copy /b *.ts %s.mp4" % name)
                self.gui.download_text.insert(END, "%s合并完毕\n" % name, 'Accept')
                self.gui.download_text.see(END)
                shutil.move("%s/%s.mp4" % (path, name), "%s.mp4" % path)
                os.chdir('E:/')
                shutil.rmtree(path)
                return
            else:
                time.sleep(1)

    # 5.run
    def run(self):
        self.url = self.gui.url_text
        self.url = self.video_url()
        m3u8_list = self.get_m3u8_list()
        idx = 1
        for m3u8 in m3u8_list:
            ts_url = self.get_ts(m3u8)
            ts_list = ts_url[0]  # 获取到第几集的ts_list
            m3u8 = ts_url[1]
            num = ""
            if len(m3u8_list) == 1:
                num = self.name
            else:
                num = "第%s集" % idx
            self.download_thread(m3u8, ts_list, num)
            idx += 1

    # 6 得到视频url
    def video_url(self):
        video_id = self.url.split('/')[len(self.url.split('/')) - 1][:-5]
        url = "https://www.88ys.com/vod-play-id-%s-src-1-num-1.html" % video_id
        return url


if __name__ == '__main__':
    rt = Tk()
    ft = tf.Font(family='JetBrains Mono', size=10, weight=tf.BOLD)
    s_v = Spider_Video(rt)
    threading.Thread(target=s_v.wait_begin).start()
    rt.mainloop()
