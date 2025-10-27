from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
from tkinter import Toplevel, Frame, Label, Button, messagebox, Entry
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.views.stampa_izvestaja import StampaIzvestaja


class ZavrsniRacunElektronski:

    def rezultat_upita(self, pocetni, krajnji):
        connect = StavkaNalogaController()
        rezultat = connect.prikazi_podatke_glavna_knjiga(pocetni, krajnji)
        return rezultat

    def kreiraj_zavrsni_racun_elektronski(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year

        if pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_zavrsni_racun_elektronski)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Izveštaj možete da dobijete u okviru jedne kalendarske godine!", parent=self.prozor_zavrsni_racun_elektronski)
        else:
            try:
                # Treba da pronadjem podatke
                rezultat = self.rezultat_upita(pocetni, krajnji)
                # Dobijene podatke poslati na stampu
                stampa = StampaIzvestaja()
                stampa.stampa_glavne_knjige(rezultat, pocetni, krajnji)
                # self.rezultat_kartice_konta = self.__pronadji_karticu(konto, pocetni, krajnji)
            except OSError:
                messagebox.showwarning("Greška", "Morate zatvoriti prethodno kreiran JSON fajl!", parent=self.prozor_zavrsni_racun_elektronski)

    def __init__(self, master):
        self.master = master
        self.prozor_zavrsni_racun_elektronski = Toplevel()
        self.prozor_zavrsni_racun_elektronski.title("KREIRANJE ZAVRŠNOG RAČUNA - JSON")
        self.prozor_zavrsni_racun_elektronski.resizable(False, False)
        self.prozor_zavrsni_racun_elektronski.grab_set()
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
        self.prozor_zavrsni_racun_elektronski.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        self.prozor_zavrsni_racun_elektronski.columnconfigure(0, weight=1)
        self.prozor_zavrsni_racun_elektronski.rowconfigure(0, weight=1)
        self.prozor_zavrsni_racun_elektronski.rowconfigure(1, weight=3)

        self.prvi_frame = Frame(self.prozor_zavrsni_racun_elektronski, bg="lightblue")
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.prvi_frame.rowconfigure(0, weight=1)
        self.prvi_frame.columnconfigure(0, weight=1)
        self.naslov = Label(self.prvi_frame, text="ZAVRŠNI RAČUN - ELEKTRONSKI IZVEŠTAJ", font="11", bg="lightblue")
        self.naslov.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.drugi_frame = Frame(self.prozor_zavrsni_racun_elektronski)
        self.drugi_frame.grid(row=1, column=0)
        self.drugi_frame.rowconfigure(0, weight=2)
        self.drugi_frame.rowconfigure(1, weight=1)
        self.drugi_frame.rowconfigure(2, weight=1)
        self.drugi_frame.columnconfigure(0, weight=1)

        self.frame_datumi = Frame(self.drugi_frame)
        self.frame_datumi.grid(row=0, column=0, sticky="nsew")
        self.frame_datumi.rowconfigure(0, weight=1)
        self.frame_datumi.rowconfigure(1, weight=1)
        self.frame_datumi.columnconfigure(0, weight=1)
        self.frame_datumi.columnconfigure(1, weight=1)
        self.label_datum_od = Label(self.frame_datumi, text="Datum od:")
        self.label_datum_od.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        self.label_datum_do = Label(self.frame_datumi, text="Datum do:")
        self.label_datum_do.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        # Input polje za unos datuma od
        self.datum_od = DateEntry(self.frame_datumi, selectmode='day', locale='sr_RS',
                                  date_pattern='dd.MM.yyyy', font="8")
        self.datum_od.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.frame_datumi, selectmode='day', locale='sr_RS',
                                  date_pattern='dd.MM.yyyy', font="8")
        self.datum_do.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.frame_id = Frame(self.drugi_frame)
        self.frame_id.grid(row=1, column=0, sticky="nsew")
        self.frame_id.rowconfigure(0, weight=1)
        self.frame_id.columnconfigure(0, weight=1)
        self.frame_id.columnconfigure(1, weight=1)
        self.id_dokumenta_label = Label(self.frame_id, text="Unesi ID dokumenta:")
        self.id_dokumenta_label.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        self.id_dokumenta_entry = Entry(self.frame_id, font="8")
        self.id_dokumenta_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.frame_dugme = Frame(self.drugi_frame)
        self.frame_dugme.grid(row=2, column=0, sticky="nsew")
        self.frame_dugme.rowconfigure(0, weight=1)
        self.frame_dugme.columnconfigure(0, weight=1)
        # Dugme za stampu glavne knjige
        self.dugme_kreiraj = Button(self.frame_dugme, text="Kreiraj JSON fajl", bg="#265073", fg="white", command=self.kreiraj_zavrsni_racun_elektronski)
        self.dugme_kreiraj.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
