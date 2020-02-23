import requests
import user_agent_list
import re
import random


def getheader():
    header = user_agent_list.getheaders()
    return header


def random_free_proxy():
    while 1:
        free_proxy_str = random.choice(HTTPS)
        free_proxy_dict = eval(free_proxy_str)
        result = requests.get("https://www.baidu.com", headers=header, proxies=free_proxy_dict)
        if (result.status_code == 200):
            return free_proxy_dict


url = "https://www.xicidaili.com/nn/"
header = getheader()
response = requests.get(url, headers=header)
data = response.content.decode("utf-8")
div = re.findall(r'<table id="ip_list">.*?</table>', data, re.S)[0]
tr = re.findall(r'<tr class="odd">(.*?)</tr>', div, re.S)
tr = tr + re.findall(r'<tr class="">(.*?)</tr>', div, re.S)
HTTP=[]
HTTPS=[]
for td_list in tr:
    td = re.findall(r'<td>(.*?)</td>', td_list)
    if(td[2] == "HTTP"):
        HTTP.append("{\'http\':\'%s:%s\'}" % (td[0], td[1]))
    else:
        HTTPS.append("{\'http\':\'%s:%s\'}" % (td[0], td[1]))
#with open("西刺免费代理.txt", "w", encoding="utf-8") as f:
#   f.write("HTTP\n")
#    for element in HTTP:
#        f.write(element+"\n")
#    f.write("HTTPS\n")
#    for element in HTTPS:
#        f.write(element+"\n")


