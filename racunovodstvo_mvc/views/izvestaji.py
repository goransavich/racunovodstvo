from tkinter import Button, LabelFrame
from racunovodstvo_mvc.views.stanje_konta import StanjeKonta
from racunovodstvo_mvc.views.kartica_konta import KarticaKonta
from racunovodstvo_mvc.views.izvrsenje_budzeta import IzvrsenjeBudzeta
from racunovodstvo_mvc.views.zakljucni_list import ZakljucniList
from racunovodstvo_mvc.views.dnevnik_knjizenja import DnevnikKnjizenja
from racunovodstvo_mvc.views.glavna_knjiga import GlavnaKnjiga
from racunovodstvo_mvc.views.knjiga_dobavljaca import KnjigaDobavljaca
from racunovodstvo_mvc.views.placeni_avansi import PlaceniAvansi


# Polje sa dugmadima za izvestaje
class Izvestaji:

    def __otvori_stanje_konta(self):
        StanjeKonta(self.master)

    def __otvori_kartica_konta(self):
        KarticaKonta(self.master)

    def __otvori_izvrsenje_budzeta(self):
        IzvrsenjeBudzeta(self.master)

    def __otvori_zakljucni_list(self):
        ZakljucniList(self.master)

    def __otvori_dnevnik_knjizenja(self):
        DnevnikKnjizenja(self.master)

    def __otvori_glavnu_knjigu(self):
        GlavnaKnjiga(self.master)

    def __otvori_knjigu_dobavljaca(self):
        KnjigaDobavljaca(self.master)

    def __otvori_placene_avanse(self):
        PlaceniAvansi(self.master)

    def __init__(self, master):
        self.master = master
        self.izvestaji_frame = LabelFrame(text="Izveštaji", bg="lightblue")
        self.izvestaji_frame.grid(row=3, column=0, padx=10, pady=10, ipady=10, sticky="nsew")
        self.stanje_konta = Button(self.izvestaji_frame, text="Stanje po kategorijama", command=self.__otvori_stanje_konta, bg="#265073", fg="white")
        self.stanje_konta.grid(row=0, column=0, padx=(10, 1), pady=10, sticky="w")
        self.kartica_konta = Button(self.izvestaji_frame, text="Kartica konta", command=self.__otvori_kartica_konta, bg="#265073", fg="white")
        self.kartica_konta.grid(row=0, column=1, pady=10, sticky="w")
        self.izvrsenje_budzeta = Button(self.izvestaji_frame, text="Izvršenje budžeta", command=self.__otvori_izvrsenje_budzeta, bg="#265073", fg="white")
        self.izvrsenje_budzeta.grid(row=0, column=2, padx=(1, 1), pady=10, sticky="w")
        self.zakljucni_list = Button(self.izvestaji_frame, text="Zaključni list", command=self.__otvori_zakljucni_list, bg="#265073", fg="white")
        self.zakljucni_list.grid(row=0, column=3, pady=10, sticky="w")
        self.dnevnik_knjizenja = Button(self.izvestaji_frame, text="Dnevnik knjiženja", command=self.__otvori_dnevnik_knjizenja, bg="#265073", fg="white")
        self.dnevnik_knjizenja.grid(row=0, column=4, padx=1, pady=10, sticky="w")
        self.glavna_knjiga = Button(self.izvestaji_frame, text="Glavna knjiga", command=self.__otvori_glavnu_knjigu, bg="#265073", fg="white")
        self.glavna_knjiga.grid(row=0, column=5, pady=10, sticky="w")
        self.knjiga_dobavljaca = Button(self.izvestaji_frame, text="Knjiga dobavljača", command=self.__otvori_knjigu_dobavljaca, bg="#265073", fg="white")
        self.knjiga_dobavljaca.grid(row=0, column=6, pady=10, sticky="w")
        self.placeni_avansi = Button(self.izvestaji_frame, text="Plaćeni avansi", command=self.__otvori_placene_avanse, bg="#265073", fg="white")
        self.placeni_avansi.grid(row=0, column=7, padx=1, pady=10, sticky="w")
