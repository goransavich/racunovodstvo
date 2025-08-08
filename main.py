# Importing tk library
from racunovodstvo_mvc.views.mainwindow import MainWindow
from racunovodstvo_mvc.views.podesavanja import Podesavanja
from racunovodstvo_mvc.views.izvestaji import Izvestaji
from racunovodstvo_mvc.views.nalozi import Nalozi
from racunovodstvo_mvc.views.godinaframe import GodinaFrame
#import faulthandler

#import wmi
import os
from tkinter import messagebox
from tkinter import *
# faulthandler.enable() - OVO MOZE DA SE KORISTI DA SE VIDI GDE JE GRESKA *** ODLICNA STVAR ***

# root window
root = Tk()
'''Ovo je u slucaju da je aplikacija otvorena i minimizirana po je ponovo pokusano pokretanje'''
# if "main.exe" in [x.Name for x in wmi.WMI().Win32_Process()]:

root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=4)

# Definisan glavni prozor
main_window = MainWindow(root)
# Izbor godine
godina_frame = GodinaFrame(root)
godina_frame.prikazi_frame_godina()
aktivna_godina = godina_frame.trenutna_godina()
# Polje podesavanja
podesavanja = Podesavanja(root)

# Polje nalozi
nalozi = Nalozi(root)
nalozi.prikazi_naloge(aktivna_godina)

# Polje Izvestaji
izvestaji = Izvestaji(root)

root.mainloop()
