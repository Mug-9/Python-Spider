import requests
import spider_xici_free_proxy
import user_agent_list
import re

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
    'username':'xx',
    'password':'xx'
}
free_proxy = spider_xici_free_proxy.random_free_proxy()
print(free_proxy)
response = session.post(login_url, headers=user_agent_list.getheaders(), proxies=free_proxy, data=login_data)
print(response.status_code)
data = session.get(member_url, headers=user_agent_list.getheaders()).content.decode()

with open('awewall.html', 'w') as f:
    f.write(data)