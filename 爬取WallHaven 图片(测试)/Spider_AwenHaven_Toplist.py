import requests
import re
from user_agent_list import getheaders
from spider_xici_free_proxy import random_free_proxy
from bs4 import BeautifulSoup
import time

class Spider_AwenHaven_Toplist(object):
    def __init__(self):
        self.login_url = "https://wallhaven.cc/auth/login"
        self.toplist_url = "https://wallhaven.cc/toplist"
        self.user_agent = getheaders()
        print(" user_agent 获取完毕!!!\n user-agent: %s" % self.user_agent)
        self.proxy = random_free_proxy()
        self.cookie_dict={}
        print(" proxy获取完毕!!!\n proxy: %s" % self.proxy)

    #1.发请求
    #1.1组装login_data
    def Assemble_login_data(self, _token):
        print(" login_data 开始组装...")
        login_data = {
            '_token': _token,
            'username': '643719884@qq.com',
            'password': 'dhl643719884'
        }
        print(" login_data 组装完成!!!\n login_data: %s" % login_data)
        return login_data

    #1.2 登录&获取remeber_web
    def login(self, login_data):
        print(" 开始模拟登录...")
        response = self.loop_post(self.login_url, login_data)
        self.check(response)
        print(" 登录成功!!!\n 正在组装Cookies...")
        cook = response.request.headers["Cookie"]
        temp_cookie = self.user_agent['Cookie']
        temp_cookie_list = temp_cookie.split(";")
        self.cookie_dict.update(__cfduid=temp_cookie_list[0].split('=')[1])
        cookies_list = cook.split("; ")
        for cookie in cookies_list:
            self.cookie_dict[cookie.split('=')[0]] = cookie.split('=')[1]
        self.user_agent.pop('Cookie')
        print(" cookie组装完毕!!!\n status_code: %s" % response.status_code)

    #1.3 获取页面数据
    def get_web(self, real_url):
        print(" 开始获取页面数据...")
        response = self.loop_get(real_url)
        self.check(response)
        print(" response 获取完成!!!\n 开始解析...")
        web_data = response.content.decode("utf-8")
        print(" 页面数据获取完毕!!!")
        return web_data

    #1.4 loop 获取页面数据
    def loop_get(self, url):
        loop = 20
        while (loop):
            try:
                response = requests.get(url, headers=self.user_agent, proxies=self.proxy, timeout=5, cookies=self.cookie_dict)
                print(' 链接成功!!!')
                break
            except requests.exceptions.RequestException as e:
                loop = loop - 1
                print(" 链接失败,重新连接,%s 次后放弃..." % loop)
        if loop == 0:
            response = -1
       # self.check(response)
        return response

    #1.5 loop_post
    def loop_post(self, url, login_data):
        loop = 20
        while (loop):
            try:
                response = requests.post(url, headers=self.user_agent, proxies=self.proxy, data=login_data, timeout=5)
                print(' 链接成功!!!')
                return response
            except requests.exceptions.RequestException as e:
                loop = loop - 1
                print(" 链接失败,重新连接,%s 次后放弃..." % loop)
        if loop == 0:
            response = -1
       # self.check(response)
        return response

    #2.解析数据
    #2.1 解析_token & 获取登录cookie
    def Analysis_token(self):
        print(" _token 开始获取...")
        response = self.loop_get("https://wallhaven.cc/login")
        print(" _token response完毕!!!")
        data = response.content.decode("utf-8")
        print(" _token data解析完成!!!")
        soup = BeautifulSoup(data, 'lxml')
        _token = soup.find_all(type='hidden')[0]['value']
        cookie = ""
        for c in response.cookies:
            cookie += c.name + "=" + c.value + ";"
        self.user_agent['Cookie'] = cookie
        print(" _token获取完毕!!!\n _token: %s" % _token)
        return _token

    #2.2 解析页面数据获取img_web_url
    def Analysis_web_data(self, web_data):
        print(" 开始解析img_web_url...")
        img_web_list = re.findall(r'<a class="preview" href="(.*?)"  target="_blank"  ></a>', web_data)
        print(" 页面解析完成")
        return img_web_list

    #2.3 解析img_url
    def Analysis_img_url(self, web_url):
        print(" 开始解析img_url...")
        response = self.loop_get(web_url).content.decode("utf-8")
        soup = BeautifulSoup(response, 'lxml')
        img_url = soup.select("#wallpaper")[0].get('src')
        print(' img_url解析完成')
        return img_url


    #3.本地
    def img_parse(self, img_url, img_name):
        print(" 开始下载图片...")
        response = self.loop_get(img_url)
        if(type(response) == type(-1) and response == -1):
            return -1
        img_data = response.content
        with open("picture//%s" % img_name, "wb") as f:
            f.write(img_data)
            print(" %s 正在写入..." % img_name)
            time.sleep(1)
            print(" %s 写入完毕" % img_name)


    #4.启动
    def run(self):
        _token = self.Analysis_token()
        login_data = self.Assemble_login_data(_token)
        self.login(login_data)
        page = 1
        while page < 167:
            real_url = self.toplist_url + "?page=%s" % page
            web_data = self.get_web(real_url)
            with open("web_data.html", "w") as f:
                f.write(web_data)
            img_web_list = self.Analysis_web_data(web_data)
            for web_url in img_web_list:
                img_url = self.Analysis_img_url(web_url)
                img_name = img_url.split('/')[5]
                print(" img_url: %s, img_name: %s" % (img_url, img_name))
                self.img_parse(img_url, img_name)
            page += 1

    #5.check
    def check(self, status_code):
        if(type(status_code) == type(-1) and status_code == -1):
            print(" 链接失败, 请重新开始")
            exit()

Spider_AwenHaven_Toplist().run()
