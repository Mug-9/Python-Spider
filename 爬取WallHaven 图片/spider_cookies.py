import requests
import re
import loopRequest


class SpiderCookies():
    def __init__(self):
        self.get_url = "https://wallhaven.cc/login"
        self.post_url = "https://wallhaven.cc/auth/login"
        self.request = loopRequest.request
        self.data = {}
        self._token = ""
        self.cookies = {}
        self.Is = False
        self.update()

    # 1. 请求页面获得_token 和 cookie
    def get_html(self):
        response = self.request.get(self.get_url)
        response_data = response.content.decode('utf-8')

        self._token = re.findall(r'<meta name="csrf-token" content="(.*?)">', response_data, re.S)

        cookies = ""
        for cookie in response.cookies:
            cookies += cookie.name + "=" + cookie.value + ";"

        # 用header来携带cookie
        self.request.proxies.header['Cookie'] = cookies

    # 2.装填data
    def combined_data(self):
        self.data = {
            '_token': self._token,
            'username': '643719884@qq.com',
            'password': 'dhl643719884'
        }

    # 3. 组装cookie
    def combined_cookie(self):
        response = self.request.post(self.post_url, data=self.data)

        # 这里拿到的cookie是相对比较齐全的cookie，主要用这个cookie来组装
        post_cookies = response.request.headers['Cookie']
        post_cookies_list = post_cookies.split("; ")

        # 这里cookie只要__cfduid
        temp_cookie = self.request.proxies.header['Cookie']
        temp_cookie_list = temp_cookie.split(";")

        # 组装
        self.cookies.update(__cfduid = temp_cookie_list[0].split('=')[1])
        for cookie in post_cookies_list:
            self.cookies[cookie.split('=')[0]] = cookie.split('=')[1]

        # header pop掉Cookie
        self.request.proxies.header.pop('Cookie')

    # 4.登录
    def post_html(self):
        response = self.request.get(self.post_url, cookies=self.cookies)
        response_data = response.content.decode('utf-8')
        if response.status_code == 200:
            print("WallPaper: Cookies获取成功")
            self.Is = True
        else:
            print("WallPaper: Cookies获取失败")

    def update(self):
        self.get_html()
        self.combined_data()
        self.combined_cookie()
        self.post_html()
