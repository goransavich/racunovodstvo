from tkinter import Toplevel, LabelFrame, Frame, Canvas, ttk, Label, Button, messagebox
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.views.stampa_izvestaja import StampaIzvestaja
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
import pandas as pd
import numpy as np
import locale
import tkinter as tk
import os


# Polje sa dugmadima za izvestaje
class ZakljucniList:

    # Pomocna funkcija za prikaz podataka u tabeli
    def __prikaz_podataka_u_tabeli(self, rezultat_stavke):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog

        # Ovo mora u slucaju da izabrani period za zakljucni list nema podataka, pa da se izbegne prijava greske
        if rezultat_stavke is not None:
            self.tree_tabela_zakljucni.delete(*self.tree_tabela_zakljucni.get_children())
            # Pretraga baze za stavkama naloga
            # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli

            self.tree_tabela_zakljucni.tag_configure('oddrow', background="white")
            self.tree_tabela_zakljucni.tag_configure('evenrow', background="lightblue")
            # self.podaci_tabela.set(rezultat_stavke)
            count_stavke_naloga = 0

            for record in rezultat_stavke:

                pocetno_duguje = locale.format_string('%10.2f', record[2], grouping=True)
                pocetno_potrazuje = locale.format_string('%10.2f', record[3], grouping=True)
                tekuce_duguje = locale.format_string('%10.2f', record[4], grouping=True)
                tekuce_potrazuje = locale.format_string('%10.2f', record[5], grouping=True)
                ukupno_duguje = locale.format_string('%10.2f', record[6], grouping=True)
                ukupno_potrazuje = locale.format_string('%10.2f', record[7], grouping=True)
                saldo_duguje = locale.format_string('%10.2f', record[8], grouping=True)
                saldo_potrazuje = locale.format_string('%10.2f', record[9], grouping=True)

                if count_stavke_naloga % 2 == 0:
                    self.tree_tabela_zakljucni.insert(parent='', index='end', iid=count_stavke_naloga, text='',
                                                   values=(record[0], record[1], pocetno_duguje, pocetno_potrazuje, tekuce_duguje, tekuce_potrazuje, ukupno_duguje, ukupno_potrazuje, saldo_duguje, saldo_potrazuje),
                                                   tags=('evenrow',))
                else:
                    self.tree_tabela_zakljucni.insert(parent='', index='end', iid=count_stavke_naloga, text='',
                                                   values=(record[0], record[1], pocetno_duguje, pocetno_potrazuje, tekuce_duguje, tekuce_potrazuje, ukupno_duguje, ukupno_potrazuje, saldo_duguje, saldo_potrazuje),
                                                   tags=('oddrow',))
                count_stavke_naloga += 1

    def __izvuci_zakljucni_list(self, pocetni_datum, krajnji_datum):
        godina = pocetni_datum.year
        rezultat = []
        konto_conn = KontoController()
        for i in range(1, 7):
            slog = konto_conn.zakljucni_list(i, pocetni_datum, krajnji_datum, godina)
            rezultat.append(slog)

        return rezultat

    def __formiraj_zakljucni_list(self, pocetni, krajnji):
        rezultat = self.__izvuci_zakljucni_list(pocetni, krajnji)
        # Ova provera mora u slucaju da za izabrani period nema podataka, da ne bi prijavljivao gresku u dataframe
        if len(rezultat[0]) == 0 and len(rezultat[1]) == 0 and len(rezultat[2]) == 0 and len(rezultat[3]) == 0 and len(rezultat[4]) == 0 and len(rezultat[5]) == 0:
            self.tree_tabela_zakljucni.delete(*self.tree_tabela_zakljucni.get_children())
            messagebox.showwarning("Obaveštenje", "Nema podataka za izabrani period!", parent=self.prozor_zakljucni_list)
            return None
        else:
            out = [item for t in rezultat for item in t]
            df = pd.DataFrame(out)
            df[0] = df[0].str.ljust(6, '0')
            df = df.sort_values(by=[0])
            df[7] = np.where((df[5] > df[6]), df[5] - df[6], 0)
            df[8] = np.where((df[5] < df[6]), df[6] - df[5], 0)
            konto_conn = KontoController()
            konta = []
            for i in df[0]:
                pronadjen_konto = konto_conn.find_oznaka(i)
                konta.append(pronadjen_konto)

            nazivi_konta = []
            for i in konta:
                nazivi_konta.append(i[0][0])

            # ubacivanje kolone sa nazivima konta u dataframe
            df.insert(1, 'naziv', nazivi_konta)
            # pravljenje liste od dataframe
            vrednosti_zakljucni = df.values.tolist()
            return vrednosti_zakljucni

    # Prikaz zakljucnog lista
    def prikazi(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year

        if pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_zakljucni_list)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Zaključni list možete da dobijete u okviru jedne kalendarske godine!", parent=self.prozor_zakljucni_list)
        else:
            podaci = self.__formiraj_zakljucni_list(pocetni, krajnji)
            self.__prikaz_podataka_u_tabeli(podaci)

    def stampaj_zakljucni(self):
        try:
            pocetni = self.datum_od.get_date()
            krajnji = self.datum_do.get_date()
            stampanje = StampaIzvestaja()
            stampanje.stampa_zakljucni_list(self.__formiraj_zakljucni_list(pocetni, krajnji), pocetni, krajnji)
        except OSError:
            messagebox.showwarning("Greška", "Morate zatvoriti prethodni PDF izveštaj!", parent=self.prozor_zakljucni_list)

    def stampaj_excel(self):
        try:
            pocetni = self.datum_od.get_date()
            krajnji = self.datum_do.get_date()
            podaci = self.__formiraj_zakljucni_list(pocetni, krajnji)
            stampanje = StampaIzvestaja()
            stampanje.zakljucni_list_excel(podaci, pocetni, krajnji)
        except:
            messagebox.showwarning("Greška", "Verovatno već imate otvoren izveštaj!", parent=self.prozor_zakljucni_list)

    def __init__(self, master):
        self.master = master
        self.prozor_zakljucni_list = Toplevel(self.master)
        self.prozor_zakljucni_list.title("IZVEŠTAJI - Zaključni list")
        self.prozor_zakljucni_list.resizable(False, False)
        self.prozor_zakljucni_list.grab_set()
        # window_width = self.master.winfo_screenwidth() - 400
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        '''
        if self.master.winfo_screenwidth() < 1400:
            window_width = self.master.winfo_screenwidth() - 120
        else:
            window_width = self.master.winfo_screenwidth() - 400

        if self.master.winfo_screenheight() < 800:
            window_height = self.master.winfo_screenheight() - 140
        else:
            window_height = self.master.winfo_screenheight() - 400
        '''
        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_zakljucni_list()
        window_height = dimenzije.odredi_visinu_zakljucni_list()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_zakljucni_list.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_zakljucni_list.columnconfigure(0, weight=1)
        self.prozor_zakljucni_list.rowconfigure(0, weight=1)
        self.prozor_zakljucni_list.rowconfigure(1, weight=6)
        self.prozor_zakljucni_list.rowconfigure(2, weight=1)

        # Prvi frame za unos podataka koji su potrebni za formiranje tabele
        self.prvi_frame = Frame(self.prozor_zakljucni_list)
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=(2, 10), sticky='nsew')
        self.prvi_frame.columnconfigure(0, weight=1)
        self.prvi_frame.rowconfigure(0, weight=1)
        self.izbor_datuma = LabelFrame(self.prvi_frame, text="Izbor datuma", bg="lightblue")
        self.izbor_datuma.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.izbor_datuma.columnconfigure(0, weight=1)
        self.izbor_datuma.columnconfigure(1, weight=1)
        self.izbor_datuma.columnconfigure(2, weight=1)
        self.izbor_datuma.columnconfigure(3, weight=1)
        self.izbor_datuma.columnconfigure(4, weight=1)
        self.izbor_datuma.columnconfigure(5, weight=1)
        self.izbor_datuma.rowconfigure(0, weight=1)
        self.izbor_datuma.rowconfigure(1, weight=1)

        # Label Datum od
        self.datum_od_text = Label(self.izbor_datuma, text="Datum od:", bg="lightblue")
        self.datum_od_text.grid(row=0, column=1, padx=10, sticky="w")
        # Label Datum do
        self.datum_do_text = Label(self.izbor_datuma, text="Datum do:", bg="lightblue")
        self.datum_do_text.grid(row=0, column=3, padx=10, sticky="w")

        # Input polje za unos datuma od
        self.datum_od = DateEntry(self.izbor_datuma, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font="8")
        self.datum_od.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.izbor_datuma, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font="8")
        self.datum_do.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Dugme za pokretanje trazenja
        self.pretrazi = Button(self.izbor_datuma, text="Prikaži", command=self.prikazi)
        self.pretrazi.grid(row=1, column=5, padx=10, pady=10, sticky='ew')

        ##########################################################################################
        # Drugi frame - tabela
        self.drugi_frame = Frame(self.prozor_zakljucni_list)
        self.drugi_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.drugi_frame.columnconfigure(0, weight=1)
        self.drugi_frame.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_tabela_zakljucni = Canvas(self.drugi_frame)
        self.canvas_tabela_zakljucni.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_zakljucni.columnconfigure(0, weight=1)
        self.canvas_tabela_zakljucni.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25, fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])
        self.tree_tabela_zakljucni = ttk.Treeview(self.canvas_tabela_zakljucni)
        self.tree_tabela_zakljucni.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.tree_tabela_zakljucni['columns'] = ("Konto", "Naziv konta", "Početno duguje", "Početno potražuje", "Tekuće duguje", "Tekuće potražuje", "Ukupno duguje", "Ukupno potražuje", "Saldo duguje", "Saldo potražuje")
        self.tree_tabela_zakljucni.column("#0", width=0, stretch=False)
        self.tree_tabela_zakljucni.column("Konto", anchor=tk.CENTER, width=100)
        self.tree_tabela_zakljucni.column("Naziv konta", anchor=tk.W, width=200)
        self.tree_tabela_zakljucni.column("Početno duguje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Početno potražuje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Tekuće duguje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Tekuće potražuje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Ukupno duguje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Ukupno potražuje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Saldo duguje", anchor=tk.E, width=100)
        self.tree_tabela_zakljucni.column("Saldo potražuje", anchor=tk.E, width=100)
        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_zakljucni)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_zakljucni.yview)
        self.tree_tabela_zakljucni.configure(yscrollcommand=self.treeScroll.set)

        self.tree_tabela_zakljucni.heading("#0", anchor=tk.W, text="")
        self.tree_tabela_zakljucni.heading("Konto", anchor=tk.CENTER, text="Konto")
        self.tree_tabela_zakljucni.heading("Naziv konta", anchor=tk.CENTER, text="Naziv konta")
        self.tree_tabela_zakljucni.heading("Početno duguje", anchor=tk.CENTER, text="Početno duguje")
        self.tree_tabela_zakljucni.heading("Početno potražuje", anchor=tk.CENTER, text="Početno potražuje")
        self.tree_tabela_zakljucni.heading("Tekuće duguje", anchor=tk.CENTER, text="Tekuće duguje")
        self.tree_tabela_zakljucni.heading("Tekuće potražuje", anchor=tk.CENTER, text="Tekuće potražuje")
        self.tree_tabela_zakljucni.heading("Ukupno duguje", anchor=tk.CENTER, text="Ukupno duguje")
        self.tree_tabela_zakljucni.heading("Ukupno potražuje", anchor=tk.CENTER, text="Ukupno potražuje")
        self.tree_tabela_zakljucni.heading("Saldo duguje", anchor=tk.CENTER, text="Saldo duguje")
        self.tree_tabela_zakljucni.heading("Saldo potražuje", anchor=tk.CENTER, text="Saldo potražuje")
        # Treci frame dugme za štampu
        # Drugi frame - tabela
        self.treci_frame = Frame(self.prozor_zakljucni_list)
        self.treci_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.treci_frame.columnconfigure(0, weight=1)
        self.treci_frame.columnconfigure(1, weight=1)
        self.treci_frame.rowconfigure(0, weight=1)
        self.dugme_za_stampu = Button(self.treci_frame, text="Štampa", bg="#265073", fg="white", command=self.stampaj_zakljucni)
        self.dugme_za_stampu.grid(row=2, column=0, padx=10, sticky='e')
        self.export_u_excel = Button(self.treci_frame, text="Eksport u excel", bg="#265073", fg="white", command=self.stampaj_excel)
        self.export_u_excel.grid(row=2, column=1, sticky='w')
