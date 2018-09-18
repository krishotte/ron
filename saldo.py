import requests
from lxml import html
import getpass
from os import path

dir_path = path.dirname(path.realpath(__file__))        #directory where saldo.py sits
file1 = open(dir_path + '\\pwd.txt', 'r')
password = file1.read()
#password = getpass.getpass(prompt = 'heslo: ', stream=None)
payload = {
    'loginname': 'pkrssak',
    'loginpassword': password
}

def str2min(str1):
    'converts string to min int' 
    min1,min2 = str1.split(':')
    if str1[0] == '-':
        mintotal = -(int(min1)*60+int(min2))
    else:
        mintotal = int(min1)*60+int(min2)
    return mintotal

def min2str(min1):
    'converts minutes to hour string'
    if min1 >= 0:
        mins = min1%60
        hrs = min1//60
        strhrs = str(hrs)
    else:
        mins = abs(min1)%60
        hrs = abs(min1)//60
        strhrs = '-' + str(hrs)
    return strhrs+':'+str(mins).zfill(2)

class web_scrape():
    'web scraping class'
    def __init__(self):
        self.session_requests = requests.session()
    def get_tree(self, url, payload):
        """
        gets html tree from url
        provide(url, payload)
            payload = dictionary of login data
        """
        self.result = self.session_requests.post(
            url,
            data = payload,
            headers = dict(referer=url)
        )
        #print(self.result.text)
        self.tree = html.fromstring(self.result.content)
        return self.tree

class ron_data_extract():
    'extracts data from html tree'
    def __init__(self):
        self.laststart = 0
        self.leave = 0
    def get_overtime(self, tree):
        'gets overtime until today'
        self.overtime_str = tree.xpath('//tr[@class="browsercolor2 mv_110"]/td[@class="hodiny"]/text()')[0]
        self.overtime_mins = str2min(self.overtime_str)
        print('nadcas do vcera: ', self.overtime_str)
        return self.overtime_mins
    def analyze_day(self, tree):
        'decomposes day data and creates times and operations lists'
        #today1 = tree.xpath('//tr[@class="today "]/td[@class="browser_rowheader"]/text()')
        today1 = tree.xpath('//tr[@class="today "]/td/text()')
        print("dnes je: ", today1[0])
        today2 = tree.xpath('//tr/td/text()')
        today3 = today1 #[0:4] #today2[6:10]
        #print('today2: ', today3)

        self.times = []
        self.operations = []
        for i in range(1, len(today3)):             #creates times and operations lists
            a, b = today3[i].split(' &nbsp ')
            self.times.append(a)
            self.operations.append(b)
        print('analyza dna:')
        print('   casy: ', self.times)
        print('   operacie', self.operations)
    def get_worktime(self):
        'calculates todays wortime'
        self.worktime = 0
        print('analyza pracovneho casu:')
        self.starts = ['Príchod / Práca', 'Vyjazd']
        self.stops = ['Súkromne', 'Obed', 'Odchod']
        a=0
        b=0
        for i in range(len(self.operations)):            #counts worktime
            #if self.operations[i] == 'Príchod / Práca':
            if a == 0 and (self.operations[i] in self.starts):
                a = str2min(self.times[i])
                self.laststart_index = i
                print('   i:', i, 'a: ', a)
            #elif a != 0 and self.operations[i] != 'Príchod / Práca':
            elif a != 0:
                b = str2min(self.times[i])
                self.lastrecord_index = i
                print('   i:', i, 'b: ', b)
                self.worktime = self.worktime + b - a
                if self.operations[i] in self.starts:
                    a = str2min(self.times[i])
                    self.laststart_index = i
                else:
                    a = 0
                b = 0
        #print('   pracovny cas do posledneho prichodu: ', min2str(self.worktime))
        return self.worktime
    def get_lunch(self):
        'calculates lunch and its correction'
        c = 0
        d = 0
        self.lunchcorrection = 0
        for i in range(len(self.operations)):            
            if self.operations[i] == 'Obed':
                c = str2min(self.times[i])
                obed_index = i
            elif (c !=0 and self.operations[i] == 'Príchod / Práca') and d==0:
                d = str2min(self.times[i])
        if d > c:
            self.lunch = d - c
        else:
            self.lunch = 30
            self.lunchcorrection = 30
        print('obed dnes: ', min2str(self.lunch))
        if self.lunch < 30:
            self.lunchcorrection = 30 - self.lunch
        print('korekcia obedovej prestavky: ', min2str(self.lunchcorrection))
        return self.lunch, self.lunchcorrection
    def get_laststart(self):
        try:
            lasttime = self.times[self.laststart_index]
        except (IndexError, AttributeError):
            lasttime = '8:00'
        try:
            if (self.laststart_index <= self.lastrecord_index) and (self.operations[self.lastrecord_index] != 'Odchod'):
                lasttime = self.times[self.lastrecord_index]
                print('chyba prichod!')
        except:
            pass
        print('posledny prichod: ', lasttime)
        return str2min(lasttime)
    def check_leave(self):
        'checks if person left the work'
        self.left = False
        for i in range(len(self.operations)):            
            if self.operations[i] == 'Odchod':
                self.left = True
        return self.left
#main script
doch_url = 'http://ron.dqi.sk/ads.php?menuid=dochazkazamestnance'
month_res_url = 'http://ron.dqi.sk/ads.php?menuid=mesicnivysledky'

wscr = web_scrape()
rde = ron_data_extract()
tree = wscr.get_tree(month_res_url, payload)
overtime = rde.get_overtime(tree)

tree = wscr.get_tree(doch_url, payload)
rde.analyze_day(tree)
worktime = rde.get_worktime()
lunch, lunchcorrection = rde.get_lunch()
laststart = rde.get_laststart()
left = rde.check_leave()
if left==True:
    overtimenew = worktime-480+overtime-lunchcorrection
    print('praca na dnes ukoncena; pracovna doba: ', min2str(worktime), '; saldo:', min2str(overtimenew))
else:
    print('   pracovny cas do posledneho prichodu: ', min2str(worktime))
    todayend = 8*60 - worktime - overtime + laststart + lunchcorrection
    print('dnes odchod, 0 saldo: ', min2str(todayend))

    todayend8hrs = 8*60 - worktime + laststart + lunchcorrection
    print('dnes odchod, 8 hodin: ', min2str(todayend8hrs))

input()