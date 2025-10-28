from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
from tkinter import Toplevel, Frame, Label, Button, messagebox, Entry
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.KorisnikController import KorisnikController
from racunovodstvo_mvc.views.aop import Aop
import os
import json


class IzvrsenjeBudzetaElektronski:

    @staticmethod
    def pronadji_ukupan_broj_izvora():
        stavke_conn = StavkaNalogaController()
        pronadjeni_izvori = stavke_conn.pronadji_izvore()
        lista_izvora = []
        for item in pronadjeni_izvori:
            if item[0] != '':
                lista_izvora.append(item[0])

        return lista_izvora

    @staticmethod
    def rezultat_upita(pocetni, krajnji):
        connect = StavkaNalogaController()
        rezultat = connect.prikazi_podatke_glavna_knjiga(pocetni, krajnji)
        return rezultat

    @staticmethod
    def svedi_na_hiljade(broj):
        if 500 < broj < 1000:
            return 1
        elif broj >= 1000:
            return round(broj / 1000)
        else:
            return 0

    def kreiranje_json_strukture(self, naziv_izvestaja):
        id_izvestaja = int(self.id_dokumenta_entry.get())
        json_data = {
            "Header": {
                "Name": naziv_izvestaja,
                "OrganizationStatus": "None",
                "OrganizationStatusChangedDate": None,
                "ReportTypePeriodId": id_izvestaja,
                "Description": ""
            },
            "Forms": [
                {
                    "Header": {
                        "Type": 5,
                        "Kind": 1
                    }
                }
            ]
        }
        return json_data

    @staticmethod
    def folder_izvestaj_izvrsenje():
        return os.getcwd() + "\\izvrsenje_budzeta\\"

    def napravi_json_fajl(self, podaci, naziv_fajla):
        putanja = os.path.join(self.folder_izvestaj_izvrsenje(), naziv_fajla + ".json")

        with open(putanja, 'w', encoding='utf-8') as fajl:
            json.dump(podaci, fajl, default=str, ensure_ascii=False, indent=4)

    @staticmethod
    def pronadji_jbkjs():
        korisnik = KorisnikController()
        izabrani_korisnik = korisnik.read()
        jbkjs = izabrani_korisnik[0][3]
        return jbkjs

    @staticmethod
    def odredi_oznaku_izvestaja(pocetni, krajnji):
        if pocetni == 1 and krajnji == 3:
            oznaka_izvestaja = "PFI1"
        elif pocetni == 1 and krajnji == 6:
            oznaka_izvestaja = "PFI2"
        elif pocetni == 1 and krajnji == 9:
            oznaka_izvestaja = "PFI3"
        elif pocetni == 1 and krajnji == 12:
            oznaka_izvestaja = "PFI4"
        else:
            oznaka_izvestaja = "neispravan period"
        return oznaka_izvestaja

    @staticmethod
    def napravi_naziv_izvestaja(oznaka, godina, jbkjs):
        return oznaka + "-" + godina + "-" + jbkjs + "-1"

    def kreiraj_izvrsenje_budzeta_elektronski(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year
        id_izvestaja = self.id_dokumenta_entry.get()
        pocetni_mesec = pocetni.month
        krajnji_mesec = krajnji.month

        if pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_izvrsenje_budzeta_elektronski)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Izveštaj možete da dobijete u okviru jedne kalendarske godine!", parent=self.prozor_izvrsenje_budzeta_elektronski)
        elif id_izvestaja == "":
            messagebox.showwarning("Greška", "Morate uneti ID izveštaja sa sajta Uprave za trezor!", parent=self.prozor_izvrsenje_budzeta_elektronski)
        else:
            try:
                # Treba da pronadjem podatke
                # izvori = self.pronadji_ukupan_broj_izvora()
                konto_conn = KontoController()
                # u ovom nizu se nalaze rashodi - konto 4 cifre i iznos
                rezultat_rashodi = konto_conn.izvrsenje_budzeta_elektronski_rashodi(pocetni, krajnji)
                # u ovom nizu se nalaze prihodi - konto 4 cifre i iznos
                rezultat_prihodi = konto_conn.izvrsenje_budzeta_elektronski_prihodi(pocetni, krajnji)
                # nizu rezultata rashoda dodajem elemente iz niza prihodi i pravim jednu listu
                for element in rezultat_prihodi:
                    rezultat_rashodi.append(element)

                # pretvoriti brojeve u hiljade
                zaokruzeni = [(konto, self.svedi_na_hiljade(b)) for konto, b in rezultat_rashodi]

                ucitaj_aop = Aop()
                # TREBA UNETI VREDNOSTI ZA KONTA U POSEBNU KLASU primer kao u mapi ispod
                mapirani_aop = ucitaj_aop.mapa
                # Kreiraj novu listu sa zamenjenim vrednostima
                nova_lista = [(mapirani_aop.get(tekst, tekst), broj) for tekst, broj in zaokruzeni]
                # KREIRANJE JSON FAJLA
                # odredjivanje naziva fajla - za koji period se pravi
                naziv_izvestaja_za_snimanje = self.napravi_naziv_izvestaja(self.odredi_oznaku_izvestaja(pocetni_mesec, krajnji_mesec), str(krajnja_godina), self.pronadji_jbkjs())
                json_data = self.kreiranje_json_strukture(naziv_izvestaja_za_snimanje)
                # Dodavanje podataka u prvi element Forms liste
                form_entry = json_data["Forms"][0]
                for key, value in nova_lista:
                    form_entry[key] = [0, value]
                # Snimanje u fajl
                # pravljenje JSON fajla
                self.napravi_json_fajl(json_data, naziv_izvestaja_za_snimanje)
                messagebox.showinfo("Uspešno", "Uspešno je formiran JSON izveštaj " + naziv_izvestaja_za_snimanje + ". Možete ga pronaći u folderu racunovodstvo/izvrsenje_budzeta.",
                                       parent=self.prozor_izvrsenje_budzeta_elektronski)
            except OSError:
                messagebox.showwarning("Greška", "Nije formiran JSON, neka greška je u pitanju!", parent=self.prozor_izvrsenje_budzeta_elektronski)

    def __init__(self, master):
        self.master = master
        self.prozor_izvrsenje_budzeta_elektronski = Toplevel()
        self.prozor_izvrsenje_budzeta_elektronski.title("KREIRANJE IZVRŠENJA BUDŽETA - JSON")
        self.prozor_izvrsenje_budzeta_elektronski.resizable(False, False)
        self.prozor_izvrsenje_budzeta_elektronski.grab_set()
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
        self.prozor_izvrsenje_budzeta_elektronski.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        self.prozor_izvrsenje_budzeta_elektronski.columnconfigure(0, weight=1)
        self.prozor_izvrsenje_budzeta_elektronski.rowconfigure(0, weight=1)
        self.prozor_izvrsenje_budzeta_elektronski.rowconfigure(1, weight=3)

        self.prvi_frame = Frame(self.prozor_izvrsenje_budzeta_elektronski, bg="lightblue")
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.prvi_frame.rowconfigure(0, weight=1)
        self.prvi_frame.columnconfigure(0, weight=1)
        self.naslov = Label(self.prvi_frame, text="IZVRŠENJE BUDŽETA - ELEKTRONSKI IZVEŠTAJ", font="11", bg="lightblue")
        self.naslov.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.drugi_frame = Frame(self.prozor_izvrsenje_budzeta_elektronski)
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
        self.dugme_kreiraj = Button(self.frame_dugme, text="Kreiraj JSON fajl", bg="#265073", fg="white", command=self.kreiraj_izvrsenje_budzeta_elektronski)
        self.dugme_kreiraj.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
