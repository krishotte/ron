import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.lang import Builder
from os import path

dir_path = path.dirname(path.realpath(__file__)) 
file_path = dir_path + "\\saldo.kv"
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())

class MainV(BoxLayout):
    pass

class Item1(BoxLayout):
    txt1 = StringProperty()
    txt2 = StringProperty()

class Saldo1(App):
    def build(self):
        vidg = MainV()
        return vidg

if __name__ == '__main__':
    Saldo1().run()