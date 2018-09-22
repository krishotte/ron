from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.lang import Builder
from os import path
import saldo
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
import time

dir_path = path.dirname(path.realpath(__file__)) 
file_path = dir_path + "\\saldo.kv"
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())

class Item1(BoxLayout):
    txt1 = StringProperty()
    txt2 = StringProperty()

class Label2(Label):
    pass

class MainV(FloatLayout):
    lbl2 = Label2()
    field1_lbl = StringProperty()
    field1_val = StringProperty()
    field2_lbl = StringProperty()
    field2_val = StringProperty()
    field3_lbl = StringProperty()
    field3_val = StringProperty()
    field4_lbl = StringProperty()
    field4_val = StringProperty()
    field5_lbl = StringProperty()
    field5_val = StringProperty()
    def showlabel(self, *args):
        self.add_widget(self.lbl2)

    def hidelabel(self, *args):
        self.remove_widget(self.lbl2)
    def run(self, *args):
        'runs main program'
        Clock.schedule_once(self.showlabel, 0)
        Clock.schedule_once(self.hidelabel, 2)
        doch_url = 'http://ron.dqi.sk/ads.php?menuid=dochazkazamestnance'
        month_res_url = 'http://ron.dqi.sk/ads.php?menuid=mesicnivysledky'

        wscr = saldo.web_scrape()
        rde = saldo.ron_data_extract()
        tree = wscr.get_tree(month_res_url, saldo.payload)
        overtime = rde.get_overtime(tree)
        try:
            tree = wscr.get_tree(doch_url, saldo.payload)
            rde.analyze_day(tree)
            worktime = rde.get_worktime()
            lunch, lunchcorrection = rde.get_lunch()
            laststart = rde.get_laststart()
            left = rde.check_leave()
            if left==True:
                overtimenew = worktime-480+overtime-lunchcorrection
                print('praca na dnes ukoncena; pracovna doba: ', saldo.min2str(worktime), '; saldo:', saldo.min2str(overtimenew))
                self.field4_lbl = 'praca na dnes ukoncena; pracovna doba: '
                self.field4_val = saldo.min2str(worktime)
                self.field5_lbl = 'saldo'
                self.field5_val = saldo.min2str(overtimenew)
            else:
                print('   pracovny cas do posledneho prichodu: ', saldo.min2str(worktime))
                todayend = 8*60 - worktime - overtime + laststart + lunchcorrection
                print('dnes odchod, 0 saldo: ', saldo.min2str(todayend))
                todayend8hrs = 8*60 - worktime + laststart + lunchcorrection
                print('dnes odchod, 8 hodin: ', saldo.min2str(todayend8hrs))
                self.field4_lbl = '0 saldo'
                self.field4_val = saldo.min2str(todayend)
                self.field5_lbl = '8 hodín'
                self.field5_val = saldo.min2str(todayend8hrs)
            self.field1_lbl = 'nadčas do včera'
            self.field1_val = saldo.min2str(overtime)
            self.field2_lbl = 'dnes je'
            self.field2_val = rde.today
            self.field3_lbl = 'obed dnes'
            self.field3_val = saldo.min2str(lunch)
        except(IndexError):
            self.field1_lbl = 'nadčas do včera'
            self.field1_val = saldo.min2str(overtime)
            self.field2_lbl = 'dnes nie je pracovný deň'
        
class Saldo1(App):
    vidg = MainV()
    def build(self):
        Window.size = (280, 160)
        self.vidg.run()
        Clock.schedule_interval(self.vidg.run, 100) #lambda dt:self.run2(), 6)
        return self.vidg

if __name__ == '__main__':
    Saldo1().run()