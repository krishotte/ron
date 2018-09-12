import requests
from lxml import html
import getpass

password = getpass.getpass(prompt = 'heslo: ', stream=None)
payload = {
    'loginname': 'pkrssak',
    'loginpassword': password
}

def str2min(str1):
    'converts string to min int'
    min1,min2 = str1.split(':')
    mintotal = int(min1)*60+int(min2)
    return mintotal

def min2str(min1):
    'converts minutes to hour string'
    mins = min1%60
    hrs = min1//60
    return str(hrs)+':'+str(mins)

session_requests = requests.session()
doch_url = 'http://ron.dqi.sk/ads.php?menuid=dochazkazamestnance'
month_res_url = 'http://ron.dqi.sk/ads.php?menuid=mesicnivysledky'
login_url = month_res_url
spr_doch = 'http://ron.dqi.sk/ads.php?menuid=zpracovanadochazka'

result = session_requests.post(
    login_url,
    data = payload,
    headers = dict(referer=login_url)
)

tree = html.fromstring(result.content)

sadlo = tree.xpath('//td[@class="hodiny"]/text()')
sadlo2 = tree.xpath('//tr[@class="browsercolor2 mv_110"]/td[@class="hodiny"]/text()')

#print(result.text)
#print('nadcas do vcera: ', sadlo2)
print('nadcas do vcera (min): ', str2min(sadlo2[0]))

login_url = doch_url
result = session_requests.get(
    login_url,
    headers = dict(referer=login_url)
)
#print(result.text)

tree = html.fromstring(result.content)
today1 = tree.xpath('//tr[@class="today "]/td[@class="browser_rowheader"]/text()')
print("today: ", today1)
today2 = tree.xpath('//tr/td/text()')
today3 = today2[6:10]
print('today2: ', today3)

times = []
operations = []
for i in range(1, len(today3)):             #creates times and operations lists
    a, b = today3[i].split(' &nbsp ')
    times.append(a)
    operations.append(b)

print(times)
print(operations)

worktime = 0
for i in range(len(operations)):            #counts worktime
    if operations[i] == 'Príchod / Práca':
        a = str2min(times[i])
        laststart = i
        print('i:', i, 'a: ', a)
    elif a != 0 and operations[i] != 'Príchod / Práca':
        b = str2min(times[i])
        print('i:', i, 'b: ', b)
        worktime = worktime + b - a
        a = 0
        b = 0
c = 0
d = 0
lunchcorrection = 0
for i in range(len(operations)):            #counts lunchtime and its correction
    if operations[i] == 'Obed':
        c = str2min(times[i])
    elif c !=0 and operations[i] == 'Príchod / Práca':
        d = str2min(times[i])
lunch = d - c
if lunch < 30:
    lunchcorrection = 30 - lunch

print('obed: ', min2str(lunch))
print('pracovny cas: ', worktime, 'mins, hrs: ', min2str(worktime))
todayend = 480 - worktime - str2min(sadlo2[0]) + str2min(times[laststart]) + lunchcorrection 
print('dnes odchod, 0 saldo: ', min2str(todayend))

todayend8hrs = 480 - worktime + str2min(times[laststart]) + lunchcorrection
print('dnes odchod, 8 hodin: ', min2str(todayend8hrs))
