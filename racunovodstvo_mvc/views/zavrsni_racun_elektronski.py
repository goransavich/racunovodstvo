from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
from tkinter import Toplevel, Frame, Label, Button, messagebox, Entry, ttk
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.controllers.GodinaController import GodinaConnection
from racunovodstvo_mvc.controllers.KontoController import KontoController
from datetime import datetime
from decimal import Decimal
from collections import defaultdict


class ZavrsniRacunElektronski:

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
        #self.godina_combo.bind('<<ComboboxSelected>>', self.promena_godine)

    def rezultat_upita(self, pocetni, krajnji):
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

    @staticmethod
    def apsolutni_iznosi(niz):
        return [(oznaka, abs(iznos)) for oznaka, iznos in niz]

    @staticmethod
    def izbaci_vrednost_nula(niz):
        return [(sifra, abs(vrednost)) for sifra, vrednost in niz if vrednost != Decimal('0.00')]

    @staticmethod
    def spoj_sve_nizove(*args):
        rezultat = defaultdict(list)

        if not args:
            return rezultat

        # Prvi niz je referentni
        prvi_niz = args[0]
        kljucevi_prvog = set(k for k, _ in prvi_niz)

        # Dodaj vrednosti iz prvog niza bez nula
        for k, v in prvi_niz:
            rezultat[k].append(v)

        # Obradi ostale nizove
        for niz in args[1:]:
            for k, v in niz:
                if k in kljucevi_prvog:
                    rezultat[k].append(v)
                else:
                    rezultat[k].append(0)
                    rezultat[k].append(v)

        return rezultat

    def kreiraj_zavrsni_racun_elektronski(self):
        # postaviti pocetni i krajnji datum zavrsnog racuna na osnovu izabrane godine
        izabrana_godina = self.godina_combo.get()
        pocetni_datum = "01-01-" + izabrana_godina
        zavrsni_datum = "31-12-" + izabrana_godina
        pocetni_datum_objekat = datetime.strptime(pocetni_datum, "%d-%m-%Y")
        zavrsni_datum_objekat = datetime.strptime(zavrsni_datum, "%d-%m-%Y")
        pocetni_datum_date = pocetni_datum_objekat.date()
        zavrsni_datum_date = zavrsni_datum_objekat.date()
        id_izvestaja = self.id_dokumenta_entry.get()
        konto_conn = KontoController()
        if id_izvestaja == "":
            messagebox.showwarning("Greška", "Morate uneti ID izveštaja sa sajta Uprave za trezor!", parent=self.prozor_zavrsni_racun_elektronski)
        else:
            # podaci za obrazac 1 - Aktiva
            # Pocetno stanje aktive - preneto iz prethodne godine
            aktiva_pocetno = konto_conn.zavrsni_racun_aktiva_pocetno(pocetni_datum_date, zavrsni_datum_date, izabrana_godina)
            vanbilansna_aktiva_pocetno = konto_conn.zavrsni_racun_vanbilansna_aktiva_pocetno(pocetni_datum_date, zavrsni_datum_date,izabrana_godina)
            # nizu rezultata aktiva dodajem elemente iz niza vanbilansna aktiva i pravim jednu listu
            for element in vanbilansna_aktiva_pocetno:
                aktiva_pocetno.append(element)

            apsolutni_iznosi_aktiva_pocetno = self.apsolutni_iznosi(aktiva_pocetno)
            zaokruzeni_aktiva_pocetno = [(konto, self.svedi_na_hiljade(b)) for konto, b in apsolutni_iznosi_aktiva_pocetno]
            # Zavrsno stanje aktive

            # podaci za obrazac 1 - Pasiva
            # Pocetno stanje pasive - preneto iz prethodne godine
            pasiva_pocetno = konto_conn.zavrsni_racun_pasiva_pocetno(pocetni_datum_date, zavrsni_datum_date, izabrana_godina)
            vanbilansna_pasiva_pocetno = konto_conn.zavrsni_racun_vanbilansna_pasiva_pocetno(pocetni_datum_date, zavrsni_datum_date, izabrana_godina)

            for element in vanbilansna_pasiva_pocetno:
                pasiva_pocetno.append(element)

            apsolutni_iznosi_pasiva_pocetno = self.apsolutni_iznosi(pasiva_pocetno)
            # pretvoriti brojeve u hiljade
            zaokruzeni_pasiva_pocetno = [(konto, self.svedi_na_hiljade(b)) for konto, b in apsolutni_iznosi_pasiva_pocetno]
            # Spajanje pocetnog stanja aktiva i pasive
            aktiva_pasiva_pocetno_ukupno = zaokruzeni_aktiva_pocetno + zaokruzeni_pasiva_pocetno
            aktiva_pasiva_pocetno = self.izbaci_vrednost_nula(aktiva_pasiva_pocetno_ukupno)
            print("aktiva pasiva pocetno:")
            print(aktiva_pasiva_pocetno)

            # Aktiva tekuce stanje
            aktiva_tekuce_bruto = konto_conn.zavrsni_racun_aktiva_tekuce_bruto(pocetni_datum_date, zavrsni_datum_date)
            # filtrirati niz i izbaciti elemente kojima je vrednost nula
            filtrirani_niz_aktiva_tekuce_bruto = self.izbaci_vrednost_nula(aktiva_tekuce_bruto)
            aktiva_tekuce_bruto_zaokruzeno = [(konto, self.svedi_na_hiljade(b)) for konto, b in filtrirani_niz_aktiva_tekuce_bruto]
            print("aktiva tekuce bruto:")
            print(aktiva_tekuce_bruto_zaokruzeno)

            # Aktiva tekuce ispravka vrednosti
            aktiva_tekuce_ispravka = konto_conn.zavrsni_racun_aktiva_tekuce_ispravka_vrednosti(pocetni_datum_date, zavrsni_datum_date)
            # filtrirati niz i izbaciti elemente kojima je vrednost nula
            filtrirani_niz_aktiva_tekuce_ispravka = self.izbaci_vrednost_nula(aktiva_tekuce_ispravka)
            aktiva_tekuce_ispravka_zaokruzeno = [(konto, self.svedi_na_hiljade(b)) for konto, b in filtrirani_niz_aktiva_tekuce_ispravka]
            print("aktiva tekuce ispravka vrednosti:")
            print(aktiva_tekuce_ispravka_zaokruzeno)

            # vanbilansna aktiva tekuce
            vanbilansna_aktiva_tekuce = konto_conn.zavrsni_racun_vanbilansna_aktiva_tekuce(pocetni_datum_date, zavrsni_datum_date)
            vanbilansna_aktiva_tekuce_zaokruzeno = [(konto, self.svedi_na_hiljade(b)) for konto, b in vanbilansna_aktiva_tekuce]
            vanbilansna_aktiva_tekuce_zaokruzeno_filtrirano = self.izbaci_vrednost_nula(vanbilansna_aktiva_tekuce_zaokruzeno)
            print("vanbilansna aktiva tekuce:")
            print(vanbilansna_aktiva_tekuce_zaokruzeno_filtrirano)

            # pasiva tekuce - saldo
            pasiva_tekuce = konto_conn.zavrsni_racun_pasiva_tekuce(pocetni_datum_date, zavrsni_datum_date)
            apsolutni_iznosi_pasiva_tekuce = self.apsolutni_iznosi(pasiva_tekuce)
            pasiva_tekuce_zaokruzeno = [(konto, self.svedi_na_hiljade(b)) for konto, b in apsolutni_iznosi_pasiva_tekuce]
            pasiva_tekuce_zaokruzeno_filtrirano = self.izbaci_vrednost_nula(pasiva_tekuce_zaokruzeno)
            print("pasiva tekuce vrednosti:")
            print(pasiva_tekuce_zaokruzeno_filtrirano)

            # vanbilansna pasiva tekuce - saldo
            vanbilansna_pasiva_tekuce = konto_conn.zavrsni_racun_vanbilansna_pasiva_tekuce(pocetni_datum_date, zavrsni_datum_date)
            apsolutni_iznosi_vanbilansna_pasiva_tekuce = self.apsolutni_iznosi(vanbilansna_pasiva_tekuce)
            vanbilansna_pasiva_tekuce_zaokruzeno = [(konto, self.svedi_na_hiljade(b)) for konto, b in apsolutni_iznosi_vanbilansna_pasiva_tekuce]
            vanbilansna_pasiva_tekuce_zaokruzeno_filtrirano = self.izbaci_vrednost_nula(vanbilansna_pasiva_tekuce_zaokruzeno)
            print("vanbilansna pasiva tekuce:")
            print(vanbilansna_pasiva_tekuce_zaokruzeno_filtrirano)

            obrazac1 = self.spoj_sve_nizove(aktiva_pasiva_pocetno, aktiva_tekuce_bruto_zaokruzeno, aktiva_tekuce_ispravka_zaokruzeno, vanbilansna_aktiva_tekuce_zaokruzeno_filtrirano, pasiva_tekuce_zaokruzeno_filtrirano, vanbilansna_pasiva_tekuce_zaokruzeno_filtrirano)
            print(obrazac1)
            print("******************************")
            for kljuc in sorted(obrazac1):
                print(f"{kljuc}: {obrazac1[kljuc]}")

            # podaci za obrazac 5 - Izvestaj o izvrsenju budzeta
            # Treba da pronadjem podatke
            # izvori = self.pronadji_ukupan_broj_izvora()
            konto_conn = KontoController()
            # u ovom nizu se nalaze rashodi - konto 4 cifre i iznos
            rezultat_rashodi = konto_conn.izvrsenje_budzeta_elektronski_rashodi(pocetni_datum_date, zavrsni_datum_date)
            # u ovom nizu se nalaze prihodi - konto 4 cifre i iznos
            rezultat_prihodi = konto_conn.izvrsenje_budzeta_elektronski_prihodi(pocetni_datum_date, zavrsni_datum_date)
            # nizu rezultata rashoda dodajem elemente iz niza prihodi i pravim jednu listu
            for element in rezultat_prihodi:
                rezultat_rashodi.append(element)
            # pretvoriti brojeve u hiljade
            zaokruzeni = [(konto, self.svedi_na_hiljade(b)) for konto, b in rezultat_rashodi]
            print(zaokruzeni)
            # Objediniti sve podatke u jedan niz


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

        self.label_datum_od = Label(self.frame_datumi, text="Završni račun za:")
        self.label_datum_od.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        '''
        self.label_datum_do = Label(self.frame_datumi, text="Datum do:")
        self.label_datum_do.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        # Input polje za unos datuma od
        self.datum_od = DateEntry(self.frame_datumi, selectmode='day', locale='sr_RS',
                                  date_pattern='dd.MM.yyyy', font="8")
        self.datum_od.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        

        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.frame_datumi, selectmode='day', locale='sr_RS',
                                  date_pattern='dd.MM.yyyy', font="8")
        self.datum_do.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        '''

        # Definisanje promenjive koja će predstavljati godinu na vrhu glavnog ekrana
        self.godina_combo = ttk.Combobox(self.frame_datumi)
        self.godina_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.prikaz_godina()

        self.id_dokumenta_label = Label(self.frame_datumi, text="Unesi ID dokumenta:")
        self.id_dokumenta_label.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.id_dokumenta_entry = Entry(self.frame_datumi, font="8")
        self.id_dokumenta_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.frame_dugme = Frame(self.drugi_frame)
        self.frame_dugme.grid(row=2, column=0, sticky="nsew")
        self.frame_dugme.rowconfigure(0, weight=1)
        self.frame_dugme.columnconfigure(0, weight=1)
        # Dugme za stampu glavne knjige
        self.dugme_kreiraj = Button(self.frame_dugme, text="Kreiraj JSON fajl", bg="#265073", fg="white", command=self.kreiraj_zavrsni_racun_elektronski)
        self.dugme_kreiraj.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
