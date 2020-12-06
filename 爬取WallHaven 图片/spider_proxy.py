import requests
import user_agent_list
from lxml import etree
import re
import random


class SpiderProxy():
    def __init__(self):
        self.url = "https://www.kuaidaili.com/free/inha/1/"
        self.header = user_agent_list.getheaders()
        self.proxy = {}

    def spider_html(self):
        response = requests.get(self.url, headers=self.header).content.decode('utf-8')
        ip_list = re.findall(r'<td data-title="IP">(.*?)</td>', response, re.S)
        port_list = re.findall(r'<td data-title="PORT">(.*?)</td>', response, re.S)
        type_list = re.findall(r'<td data-title="类型">(.*?)</td>', response, re.S)
        proxies_list = []
        for index in range(len(ip_list)):
            proxies_list.append("{\'%s\':\'%s:%s\'}" % (type_list[index], ip_list[index], port_list[index]))
        while 1:
            proxy_dict = eval(random.choice(self.proxies_list))
            response_test = requests.get(self.url, headers=self.header, proxies=proxy_dict)
            if response_test.status_code == 200:
                self.proxy = proxy_dict
                break

    def run(self):
        self.spider_html()