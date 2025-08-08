from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
from tkinter import Toplevel, Frame, Label, Button, messagebox
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.views.stampa_izvestaja import StampaIzvestaja


class GlavnaKnjiga:

    def rezultat_upita(self, pocetni, krajnji):
        connect = StavkaNalogaController()
        rezultat = connect.prikazi_podatke_glavna_knjiga(pocetni, krajnji)
        return rezultat

    def prikazi_glavnu_knjigu(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year

        if pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_glavna_knjiga)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Glavnu knjigu možete da dobijete u okviru jedne kalendarske godine!", parent=self.prozor_glavna_knjiga)
        else:
            try:
                # Treba da pronadjem podatke
                rezultat = self.rezultat_upita(pocetni, krajnji)
                # Dobijene podatke poslati na stampu
                stampa = StampaIzvestaja()
                stampa.stampa_glavne_knjige(rezultat, pocetni, krajnji)
                # self.rezultat_kartice_konta = self.__pronadji_karticu(konto, pocetni, krajnji)
            except OSError:
                messagebox.showwarning("Greška", "Morate zatvoriti prethodno otvorenu Glavnu knjigu!", parent=self.prozor_glavna_knjiga)

    def __init__(self, master):
        self.master = master
        self.prozor_glavna_knjiga = Toplevel()
        self.prozor_glavna_knjiga.title("IZVEŠTAJI - GLAVNA KNJIGA")
        self.prozor_glavna_knjiga.resizable(False, False)
        self.prozor_glavna_knjiga.grab_set()
        # window_width = self.master.winfo_screenwidth() - 800
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_glavna_knjiga()
        window_height = dimenzije.odredi_visinu_glavna_knjiga()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_glavna_knjiga.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        self.prozor_glavna_knjiga.columnconfigure(0, weight=1)
        self.prozor_glavna_knjiga.rowconfigure(0, weight=1)
        self.prozor_glavna_knjiga.rowconfigure(1, weight=3)

        self.prvi_frame = Frame(self.prozor_glavna_knjiga, bg="lightblue")
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.prvi_frame.rowconfigure(0, weight=1)
        self.prvi_frame.columnconfigure(0, weight=1)
        self.naslov = Label(self.prvi_frame, text="GLAVNA KNJIGA", font="11", bg="lightblue")
        self.naslov.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.drugi_frame = Frame(self.prozor_glavna_knjiga)
        self.drugi_frame.grid(row=1, column=0)
        self.drugi_frame.rowconfigure(0, weight=1)
        self.drugi_frame.rowconfigure(1, weight=1)
        self.drugi_frame.rowconfigure(2, weight=1)
        self.drugi_frame.columnconfigure(0, weight=1)
        self.drugi_frame.columnconfigure(1, weight=1)
        self.drugi_frame.columnconfigure(2, weight=1)
        self.drugi_frame.columnconfigure(3, weight=1)

        self.label_datum_od = Label(self.drugi_frame, text="Datum od:")
        self.label_datum_od.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        self.label_datum_do = Label(self.drugi_frame, text="Datum do:")
        self.label_datum_do.grid(row=0, column=2, padx=10, pady=10, sticky='w')

        # Input polje za unos datuma od
        self.datum_od = DateEntry(self.drugi_frame, selectmode='day', locale='sr_RS',
                                  date_pattern='dd.MM.yyyy', font="8")
        self.datum_od.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.drugi_frame, selectmode='day', locale='sr_RS',
                                  date_pattern='dd.MM.yyyy', font="8")
        self.datum_do.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        # Dugme za stampu glavne knjige
        self.dugme_stampa = Button(self.drugi_frame, text="Prikaži glavnu knjigu", bg="#265073", fg="white", command=self.prikazi_glavnu_knjigu)
        self.dugme_stampa.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky='ew')
