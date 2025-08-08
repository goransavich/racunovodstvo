from tkinter import Toplevel, LabelFrame, Frame, Canvas, ttk, Label, Button, messagebox, StringVar
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
import tkinter as tk
import pandas as pd
import os
import locale


# Polje sa dugmadima za izvestaje
class StanjeKonta:
    def poravnanje(self, vrsta):
        if vrsta == 'Sub subanalitika':
            return self.tree_tabela_stanje.column("Oznaka", anchor=tk.W, minwidth=200)
        else:
            return self.tree_tabela_stanje.column("Oznaka", anchor=tk.CENTER, minwidth=200)

    # Da se ne bi u tabeli prikazivali None ako nema broja, ova funkcija vraca 0.00
    def is_number_none(self, broj):
        if broj is None:
            return float(0)
        else:
            return broj

    def __izabrana_kategorija(self, vrsta, pocetni_datum, krajnji_datum):
        rez_kategorije = ()
        konto_conn = KontoController()
        if vrsta == "Klasa":
            rez_kategorije = konto_conn.stanje_konta_kategorije(1, pocetni_datum, krajnji_datum)
        elif vrsta == "Kategorija":
            rez_kategorije = konto_conn.stanje_konta_kategorije(2, pocetni_datum, krajnji_datum)
        elif vrsta == "Grupa":
            rez_kategorije = konto_conn.stanje_konta_kategorije(3, pocetni_datum, krajnji_datum)
        elif vrsta == "Sintetika":
            rez_kategorije = konto_conn.stanje_konta_kategorije(4, pocetni_datum, krajnji_datum)
        elif vrsta == "Analitika":
            rez_kategorije = konto_conn.stanje_konta_kategorije(5, pocetni_datum, krajnji_datum)
        elif vrsta == "Subanalitika":
            rez_kategorije = konto_conn.stanje_konta_kategorije(6, pocetni_datum, krajnji_datum)
        elif vrsta == "Sub subanalitika":
            rez_kategorije = konto_conn.stanje_kategorije_subsubanalitika(pocetni_datum, krajnji_datum)
        self.prikaz_podataka_u_tabeli(rez_kategorije)
        self.poravnanje(vrsta)

    # Pomocna funkcija za prikaz podataka u tabeli
    def prikaz_podataka_u_tabeli(self, rezultat_stavke):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog
        self.tree_tabela_stanje.delete(*self.tree_tabela_stanje.get_children())
        # Pretraga baze za stavkama naloga
        # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli

        self.tree_tabela_stanje.tag_configure('oddrow', background="white")
        self.tree_tabela_stanje.tag_configure('evenrow', background="lightblue")
        self.podaci_tabela.set(rezultat_stavke)
        count_stavke_naloga = 0

        for record in rezultat_stavke:

            duguje = locale.format_string('%10.2f', self.is_number_none(record[1]), grouping=True)
            potrazuje = locale.format_string('%10.2f', self.is_number_none(record[2]), grouping=True)
            saldo = locale.format_string('%10.2f', self.is_number_none(record[3]), grouping=True)

            if count_stavke_naloga % 2 == 0:
                self.tree_tabela_stanje.insert(parent='', index='end', iid=count_stavke_naloga, text='',
                                               values=(record[0], duguje, potrazuje, saldo),
                                               tags=('evenrow',))
            else:
                self.tree_tabela_stanje.insert(parent='', index='end', iid=count_stavke_naloga, text='',
                                               values=(record[0], duguje, potrazuje, saldo),
                                               tags=('oddrow',))
            count_stavke_naloga += 1

    def prikazi(self):
        # ovo cu aktivirati kada budem uradio automatiku za zavrsni racun
        #self.dugme_formiranje_zavrsni_racun.config(state='disabled')
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year
        kategorija = self.kategorija_combo.get()
        if kategorija == "":
            messagebox.showwarning("Greška", "Niste izabrali kategoriju!", parent=self.prozor_stanje_konta)
        elif pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!",
                                   parent=self.prozor_stanje_konta)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Karticu konta možete da dobijete u okviru jedne kalendarske godine!",
                                   parent=self.prozor_stanje_konta)
        else:
            self.__izabrana_kategorija(kategorija, pocetni, krajnji)

        # OVO AKTIVIRATI KADA URADIM AUTOMATIKU ZA ZAVRSNI RACUN
        '''
        if kategorija == 'Sintetika':
            # Treci frame dugme za formiranje fajla za zavrsni racun
            self.dugme_formiranje_zavrsni_racun.config(state='normal')
        '''

    def export_u_excel(self):
        podaci_za_excel = self.podaci_tabela.get()
        if podaci_za_excel == '':
            messagebox.showinfo("Greška", "Niste izabrali podatke!", parent=self.prozor_stanje_konta)
        else:
            df = pd.DataFrame(eval(podaci_za_excel))
            for column in df.columns[1:]:
                # Ovde se pretvaraju None vrednosti iz baze u prazno, jer pandas ne moze da pretvori None u broj
                df[column] = pd.to_numeric(df[column], errors='coerce')

            # Ovde prazne vrednosti popunjava sa nulama
            df = df.fillna(0)
            try:
                df.columns = ['Oznaka', 'Duguje', 'Potražuje', 'Saldo']
                df.to_excel('stanje_konta.xlsx', float_format='%.2f', index=False, header=True)
                os.startfile('stanje_konta.xlsx')
            except OSError:
                messagebox.showinfo("Upozorenje", "Proverite da li imate instaliran Microsoft Excel ili zatvorite prethodno otvoren excel dokument!", parent=self.prozor_stanje_konta)

    def formiraj_json(self):
        podaci = self.podaci_tabela.get()
        print(podaci)

    def __init__(self, master):
        self.master = master
        self.prozor_stanje_konta = Toplevel()
        self.prozor_stanje_konta.title("IZVEŠTAJI - Stanje po kategorijama")
        self.prozor_stanje_konta.resizable(False, False)
        self.prozor_stanje_konta.grab_set()
        # window_width = self.master.winfo_screenwidth() - 800
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_kartica_konta_stanje()
        window_height = dimenzije.odredi_visinu_kartica_konta_stanje()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_stanje_konta.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_stanje_konta.columnconfigure(0, weight=1)
        self.prozor_stanje_konta.rowconfigure(0, weight=1)
        self.prozor_stanje_konta.rowconfigure(1, weight=4)
        self.prozor_stanje_konta.rowconfigure(2, weight=1)
        self.poravnaj = ''

        # Prvi frame za unos podataka koji su potrebni za formiranje tabele
        self.prvi_frame = Frame(self.prozor_stanje_konta)
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.prvi_frame.columnconfigure(0, weight=1)
        self.prvi_frame.rowconfigure(0, weight=1)
        self.stanje_konta_kategorije = LabelFrame(self.prvi_frame, text="Pregled po kategorijama", bg="lightblue")
        self.stanje_konta_kategorije.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.stanje_konta_kategorije.columnconfigure(0, weight=1)
        self.stanje_konta_kategorije.columnconfigure(1, weight=1)
        self.stanje_konta_kategorije.columnconfigure(2, weight=1)
        self.stanje_konta_kategorije.columnconfigure(3, weight=1)
        self.stanje_konta_kategorije.columnconfigure(4, weight=1)
        self.stanje_konta_kategorije.columnconfigure(5, weight=1)
        self.stanje_konta_kategorije.rowconfigure(0, weight=1)
        self.stanje_konta_kategorije.rowconfigure(1, weight=1)
        self.podaci_tabela = StringVar()
        # Label tekst
        self.izaberi_kategoriju_text = Label(self.stanje_konta_kategorije, text="Izaberi kategoriju:", bg="lightblue")
        self.izaberi_kategoriju_text.grid(row=0, column=0, padx=10, sticky="w")
        # Label Datum od
        self.datum_od_text = Label(self.stanje_konta_kategorije, text="Datum od:", bg="lightblue")
        self.datum_od_text.grid(row=0, column=1, padx=10, sticky="w")
        # Label Datum do
        self.datum_do_text = Label(self.stanje_konta_kategorije, text="Datum do:", bg="lightblue")
        self.datum_do_text.grid(row=0, column=3, padx=10, sticky="w")
        # Combobox za izbor vrste naloga

        self.kategorija_combo = ttk.Combobox(self.stanje_konta_kategorije, font="8", background="lightblue")
        self.kategorija_combo['values'] = ('Klasa', 'Kategorija', 'Grupa', 'Sintetika', 'Analitika', 'Subanalitika', 'Sub subanalitika')
        self.kategorija_combo.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Input polje za unos datuma od
        self.datum_od = DateEntry(self.stanje_konta_kategorije, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font="8")
        self.datum_od.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.stanje_konta_kategorije, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font="8")
        self.datum_do.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Dugme za pokretanje trazenja
        self.pretrazi = Button(self.stanje_konta_kategorije, text="Prikaži", command=self.prikazi)
        self.pretrazi.grid(row=1, column=5, padx=10, pady=10, sticky='ew')

        ##########################################################################################
        # Drugi frame - tabela
        self.drugi_frame = Frame(self.prozor_stanje_konta)
        self.drugi_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.drugi_frame.columnconfigure(0, weight=1)
        self.drugi_frame.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_tabela_stanje = Canvas(self.drugi_frame)
        self.canvas_tabela_stanje.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_stanje.columnconfigure(0, weight=1)
        self.canvas_tabela_stanje.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25, fieldbackground="d3d3d3")
        # Boja selektrovanog reda

        self.style.map('Treeview', background=[('selected', '#347083')])
        self.tree_tabela_stanje = ttk.Treeview(self.canvas_tabela_stanje)
        self.tree_tabela_stanje.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.tree_tabela_stanje['columns'] = ("Oznaka", "Duguje", "Potrazuje", "Saldo")
        self.tree_tabela_stanje.column("#0", width=0, stretch=False)
        self.poravnanje("")
        self.tree_tabela_stanje.column("Duguje", anchor=tk.E, width=100)
        self.tree_tabela_stanje.column("Potrazuje", anchor=tk.E, width=100)
        self.tree_tabela_stanje.column("Saldo", anchor=tk.E, width=100)
        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_stanje)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_stanje.yview)
        self.tree_tabela_stanje.configure(yscrollcommand=self.treeScroll.set)

        self.tree_tabela_stanje.heading("#0", anchor=tk.W, text="")
        self.tree_tabela_stanje.heading("Oznaka", anchor=tk.CENTER, text="Oznaka")
        self.tree_tabela_stanje.heading("Duguje", anchor=tk.CENTER, text="Duguje")
        self.tree_tabela_stanje.heading("Potrazuje", anchor=tk.CENTER, text="Potražuje")
        self.tree_tabela_stanje.heading("Saldo", anchor=tk.CENTER, text="Saldo")

        # Treci frame dugmad
        self.treci_frame = Frame(self.prozor_stanje_konta)
        self.treci_frame.grid(row=2, column=0, padx=10, pady=0, sticky='nsew')
        self.treci_frame.columnconfigure(0, weight=1)
        self.treci_frame.columnconfigure(1, weight=1)
        self.treci_frame.rowconfigure(0, weight=1)

        # Treci frame dugme za export u excel
        self.dugme_za_export = Button(self.treci_frame, text="Eksport u excel", bg="lightblue", fg="black", command=self.export_u_excel)
        self.dugme_za_export.grid(row=0, column=0, padx=10, sticky='e')

        kategorija = self.kategorija_combo.get()
        # OVO CU AKTIVIRATI KADA BUDEM URADIO AUTOMATISKI ZA ZAVRSNI RACUN
        '''
        if kategorija == 'Sintetika':
            # Treci frame dugme za formiranje fajla za zavrsni racun
            self.dugme_formiranje_zavrsni_racun = Button(self.treci_frame, text="Formiraj JSON fajl za zavrsni racun", bg="#265073", fg="white",
                                          command=self.formiraj_json)
        else:
            self.dugme_formiranje_zavrsni_racun = Button(self.treci_frame, text="Formiraj JSON fajl za zavrsni racun",
                                                         bg="#265073", fg="white",
                                                         command=self.formiraj_json, state='disabled')
        self.dugme_formiranje_zavrsni_racun.grid(row=0, column=1, padx=10, sticky='w')
        '''