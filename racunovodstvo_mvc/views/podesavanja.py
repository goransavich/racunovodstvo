from tkinter import Button, LabelFrame
from racunovodstvo_mvc.views.vrste_naloga import VrsteNaloga
from racunovodstvo_mvc.views.konta import Konta
from racunovodstvo_mvc.views.izvori_finansiranja import IzvoriFinansiranja
from racunovodstvo_mvc.views.sistem import Sistem
from racunovodstvo_mvc.views.dobavljaci import Dobavljaci

# Polje sa dugmadima za podesavanja
class Podesavanja:
    def otvori_vrste_naloga(self):
        VrsteNaloga()

    def unesi_konto(self):
        Konta(self.master)

    def unesi_dobavljaca(self):
        Dobavljaci()

    def izvor_finansiranja(self):
        IzvoriFinansiranja()

    def sistem(self):
        Sistem(self.master)

    def __init__(self, master):
        self.master = master
        self.podesavanja_frame = LabelFrame(text="Podesavanja", bg="#eaf6f6")
        self.podesavanja_frame.grid(row=1, column=0, padx=10, sticky="ew")
        self.nalog = Button(self.podesavanja_frame, text="Vrste naloga", command=self.otvori_vrste_naloga, bg="lightblue")
        self.nalog.grid(row=0, column=0, padx=(10, 1), pady=10, sticky="w")
        self.konta = Button(self.podesavanja_frame, text="Konta", command=self.unesi_konto, bg="lightblue")
        self.konta.grid(row=0, column=1, pady=10, sticky="w")
        self.dobavljaci = Button(self.podesavanja_frame, text="Dobavljači", command=self.unesi_dobavljaca, bg="lightblue")
        self.dobavljaci.grid(row=0, column=2, pady=10, sticky="w")
        self.izvori = Button(self.podesavanja_frame, text="Izvori finansiranja", command=self.izvor_finansiranja, bg="lightblue")
        self.izvori.grid(row=0, column=3, padx=(1, 2), pady=10, sticky="w")
        self.sistem = Button(self.podesavanja_frame, text="Sistem", command=self.sistem, bg="#FFCF81")
        self.sistem.grid(row=0, column=4, pady=10, sticky="w")

