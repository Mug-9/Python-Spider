import requests
from bs4 import BeautifulSoup
from user_agent_list import getheaders

get_token_url = "https://wallhaven.cc/login"
login_url = "https://wallhaven.cc/auth/login"
member_url = "https://wallhaven.cc/user/dhl643719884"
toplist_url = "https://wallhaven.cc/toplist"
user_agent = getheaders()

session = requests.session()
response = requests.get(get_token_url, headers = user_agent)
cookie = ""
for c in response.cookies:
    cookie += c.name + "=" + c.value + ";"
user_agent['Cookie'] = cookie
html = response.content.decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
_token = soup.find_all(type='hidden')[0]['value']
post_data={
    '_token': _token,
    'username': '******',
    'password': '******'
}
response = requests.post(login_url, headers=user_agent, data=post_data)
cook = response.request.headers["Cookie"]
temp_cookie = user_agent['Cookie']
temp_cookie_list = temp_cookie.split(";")
cookie_dict={}
cookie_dict.update(__cfduid = temp_cookie_list[0].split('=')[1])
cookies_list = cook.split("; ")
for cookie in cookies_list:
    cookie_dict[cookie.split('=')[0]] = cookie.split('=')[1]
print(cookie_dict)
user_agent.pop('Cookie')
response = requests.get(toplist_url, headers=user_agent, cookies = cookie_dict)
data = response.content.decode('utf-8')
with open("awewall.html", 'w') as f:
    f.write(data)
