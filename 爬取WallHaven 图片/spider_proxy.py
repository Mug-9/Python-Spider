import requests
import user_agent_list
import re
import random


class SpiderProxy():
    def __init__(self):
        self.url = ["https://www.kuaidaili.com/free/inha/1/", "https://www.7yip.cn/free/?action=china&page=2",
                    "https://www.7yip.cn/free/?action=china&page=3", ]
        self.header = user_agent_list.getheaders()
        self.proxy = {}
        self.proxies_list = []
        self.run()

    def get_proxies_list(self, url):
        try:
            response = requests.get(url, headers=self.header, timeout=3)
            response_data = response.content.decode('utf-8')

            ip_list = re.findall(r'<td data-title="IP">(.*?)</td>', response_data, re.S)
            port_list = re.findall(r'<td data-title="PORT">(.*?)</td>', response_data, re.S)
            type_list = re.findall(r'<td data-title="类型">(.*?)</td>', response_data, re.S)

            for index in range(len(ip_list)):
                self.proxies_list.append("{\'%s\':\'%s:%s\'}" % (type_list[index], ip_list[index], port_list[index]))

        except Exception as e:
            print(e)

        # for tmp_proxy in tmp_list:
        #     proxy = eval(tmp_proxy)
        #     response = requests.get("www.baidu.com", headers=self.header, proxies=proxy)
        #     if response.status_code == 200:
        #         self.proxies_list.append(tmp_proxy)

    def get_proxy(self):
        while 1:
            try:
                self.proxy = eval(random.choice(self.proxies_list))
                response = requests.get("http://www.baidu.com", headers=self.header, proxies=self.proxy, timeout=3)
                if response.status_code == 200:
                    return
            except Exception as e:
                print("getProxy ------> ERROR", e)

    def run(self):
        for url in self.url:
            self.get_proxies_list(url)


