from racunovodstvo_mvc.controllers.GodinaController import GodinaConnection
from tkinter import ttk, Frame
from racunovodstvo_mvc.views.nalozi import Nalozi


# Polje: Izbor godine
class GodinaFrame:
    def __init__(self, master):
        self.master = master
        self.godinaframe = None
        self.godina_combo = None

    # Ova funkcija se koristi kada se unese nova godina da bi se ucitali nalozi iz te godine - odnosno dobije se prazna tabela naloga
    def promena_otvaranje_nove_godine(self):
        izabrana_godina = self.godina_combo.get()
        spisak_naloga = Nalozi(self.master)
        spisak_naloga.prikazi_naloge(izabrana_godina)

    def trenutna_godina(self):
        return self.godina_combo.get()

    def prikaz_godina(self):
        # povezivanje na bazu i preuzimanje godina iz tabele
        konekcija = GodinaConnection()
        rezultat = konekcija.read()
        sve_godine = []
        for i in rezultat:
            sve_godine.append(i[1])
        self.godina_combo['values'] = sve_godine
        # self.godina_combo['state'] = 'readonly'
        self.godina_combo.current(0)
        self.godina_combo.bind('<<ComboboxSelected>>', self.promena_godine)

    def promena_godine(self, e):
        izabrana_godina = self.godina_combo.get()
        spisak_naloga = Nalozi(self.master)
        spisak_naloga.prikazi_naloge(izabrana_godina)

    def prikazi_frame_godina(self):
        # self.master = master
        # Polje godina - prvi frame
        self.godinaframe = Frame(self.master, bg="#347083")
        self.godinaframe.grid(column=0, row=0, sticky="ew", padx=10, pady=10)
        self.godinaframe.columnconfigure(0, weight=1)
        # Definisanje promenjive koja će predstavljati godinu na vrhu glavnog ekrana
        self.godina_combo = ttk.Combobox(self.godinaframe, font=("Times", 14), width=10)
        self.godina_combo.grid(row=0, column=0, padx=10, pady=20)
        self.prikaz_godina()
        # End polje godina
