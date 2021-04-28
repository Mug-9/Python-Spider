import requests
import re
url = 'https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js'
response = requests.get(url).content.decode('utf-8')
hero_name = re.findall(r'"name":"(.*?)",', response, re.S)
names = []
for name in hero_name:
    name = name.encode('utf-8').decode("unicode_escape")
    names.append(name)
hero_title = re.findall(r'"title":"(.*?)",', response, re.S)
titles = []
for title in hero_title:
    title = title.encode('utf-8').decode("unicode_escape")
    titles.append(title)
with open('lol.txt', 'w') as f:
    for index in range(len(names)):
        print(names[index])
        f.write("%s,%s\n" % (names[index], titles[index]))
print(names)
print(titles)



