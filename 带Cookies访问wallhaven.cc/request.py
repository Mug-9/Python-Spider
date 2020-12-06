import requests
import spider_proxy
import re

proxies = spider_proxy.SpiderProxy()

session = requests.session()
login_url = "https://wallhaven.cc/auth/login"
member_url = "https://wallhaven.cc/user/dhl643719884"

def get_token():
    response = requests.get("https://wallhaven.cc/login")
    data = response.content.decode("utf-8")
    input = re.findall(r'<input type="hidden" name="_token" value=(.*?)>', data, re.S)[0]
    return input

login_data = {
    '_token': get_token(),
    'username': '643719884@qq.com',
    'password': 'dhl643719884'
}
response = session.post(login_url, headers=proxies.header, proxies=proxies.proxy, data=login_data)
print(session.cookies)
data = session.get(member_url, headers=proxies.header, proxies=proxies.proxy).content.decode()

with open('awewall.html', 'w') as f:
    f.write(data)