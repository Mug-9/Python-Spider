import requests
import urllib
import string
import user_agent_list
import re

url = "https://www.xicidaili.com/nn/"
random_user_agent = user_agent_list.getheaders()
request = urllib.request.Request(url, headers=random_user_agent)
#request.add_header("User-Agent", random_user_agent)
response = urllib.request.urlopen(request)
data = response.read().decode("utf-8")
div = re.findall(r'<table id="ip_list">.*?</table>', data, re.S)[0]
tr = re.findall(r'<tr class="odd">(.*?)</tr>', div, re.S)
tr = tr + re.findall(r'<tr class="">(.*?)</tr>', div, re.S)
HTTP=[]
HTTPS=[]
for td_list in tr:
    td = re.findall(r'<td>(.*?)</td>', td_list)
    if(td[2] == "HTTP"):
        HTTP.append("{\"http\":\"%s:%s\"}," % (td[0], td[1]))
    else:
        HTTPS.append("{\"http\":\"%s:%s\"}," % (td[0], td[1]))

with open("西刺免费代理.txt", "w", encoding="utf-8") as f:
    f.write("HTTP\n")
    for element in HTTP:
        f.write(element+"\n")
    f.write("HTTPS\n")
    for element in HTTPS:
        f.write(element+"\n")

