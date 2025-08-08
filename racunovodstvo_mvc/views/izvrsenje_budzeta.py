from tkinter import Toplevel, LabelFrame, Frame, Canvas, ttk, Label, Button, messagebox, StringVar
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
import pandas as pd
import os
import locale
import tkinter as tk


# Polje sa dugmadima za izvestaje
class IzvrsenjeBudzeta:
    # Prvo da pronadjem koliko ima izvora finansiranja
    def pronadji_ukupan_broj_izvora(self):
        stavke_conn = StavkaNalogaController()
        pronadjeni_izvori = stavke_conn.pronadji_izvore()
        lista_izvora = []
        for item in pronadjeni_izvori:
            if item[0] != '':
                lista_izvora.append(item[0])

        return lista_izvora

    # Da se ne bi u tabeli prikazivali None ako nema broja, ova funkcija vraca 0.00
    def is_number_none(self, broj):
        if broj is None:
            return float(0)
        else:
            return broj

    def __izabrana_kategorija(self, vrsta, pocetni_datum, krajnji_datum, izvori):
        rez_kategorije = ()
        konto_conn = KontoController()
        if vrsta == "Klasa":
            rez_kategorije = konto_conn.izvrsenje_budzeta(1, pocetni_datum, krajnji_datum, izvori)
        elif vrsta == "Kategorija":
            rez_kategorije = konto_conn.izvrsenje_budzeta(2, pocetni_datum, krajnji_datum, izvori)
        elif vrsta == "Grupa":
            rez_kategorije = konto_conn.izvrsenje_budzeta(3, pocetni_datum, krajnji_datum, izvori)
        elif vrsta == "Sintetika":
            rez_kategorije = konto_conn.izvrsenje_budzeta(4, pocetni_datum, krajnji_datum, izvori)
        elif vrsta == "Analitika":
            rez_kategorije = konto_conn.izvrsenje_budzeta(5, pocetni_datum, krajnji_datum, izvori)
        elif vrsta == "Subanalitika":
            rez_kategorije = konto_conn.izvrsenje_budzeta(6, pocetni_datum, krajnji_datum, izvori)
        self.prikaz_podataka_u_tabeli(rez_kategorije)

    def prikazi_tabelu(self, broj_izvora):
        self.tree_tabela_izvrsenje = ttk.Treeview(self.canvas_tabela_izvrsenje)
        self.tree_tabela_izvrsenje.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        # Ovo se koristi da bi se dinamicki odredio broj kolona, jer nemaju svi isti broj izvora finansiranja, npr. 01, 04,...
        oznake_kolona = ['Oznaka']
        for izvori in broj_izvora:
            oznake_kolona.append(izvori)

        kolone = str(" ".join('"' + item + '"' for item in oznake_kolona))
        self.tree_tabela_izvrsenje['columns'] = kolone
        self.tree_tabela_izvrsenje.column('#0', width=0, stretch=False)
        self.tree_tabela_izvrsenje.column('Oznaka', anchor=tk.CENTER, minwidth=200)

        for izvor_kolona in broj_izvora:
            self.tree_tabela_izvrsenje.column(str(izvor_kolona), anchor=tk.E, minwidth=200)

        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_izvrsenje)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_izvrsenje.yview)
        self.tree_tabela_izvrsenje.configure(yscrollcommand=self.treeScroll.set)
        self.tree_tabela_izvrsenje.heading('#0', anchor=tk.W, text="")
        self.tree_tabela_izvrsenje.heading('Oznaka', anchor=tk.CENTER, text='Oznaka')

        for izvor_zaglavlje in broj_izvora:
            self.tree_tabela_izvrsenje.heading(str(izvor_zaglavlje), anchor=tk.CENTER, text=str(izvor_zaglavlje))

    # Pomocna funkcija za prikaz podataka u tabeli
    def prikaz_podataka_u_tabeli(self, rezultat_stavke):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog
        self.tree_tabela_izvrsenje.delete(*self.tree_tabela_izvrsenje.get_children())
        # Pretraga baze za stavkama naloga
        # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli

        self.tree_tabela_izvrsenje.tag_configure('oddrow', background="white")
        self.tree_tabela_izvrsenje.tag_configure('evenrow', background="lightblue")

        self.podaci_tabela.set(rezultat_stavke)

        ukupno_kolona = len(self.pronadji_ukupan_broj_izvora())

        count_stavke_naloga = 0

        for record in rezultat_stavke:

            kolone = [record[0]]
            for i in range(1, ukupno_kolona+1):
                kolone.append(locale.format_string('%10.2f', self.is_number_none(record[i]), grouping=True))

            if count_stavke_naloga % 2 == 0:
                self.tree_tabela_izvrsenje.insert(parent='', index='end', iid=count_stavke_naloga, text='', values=kolone, tags=('evenrow',))
            else:
                self.tree_tabela_izvrsenje.insert(parent='', index='end', iid=count_stavke_naloga, text='', values=kolone, tags=('oddrow',))

            count_stavke_naloga += 1

    def prikazi(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year
        kategorija = self.kategorija_combo.get()
        if kategorija == "":
            messagebox.showwarning("Greška", "Niste izabrali kategoriju!", parent=self.prozor_stanje_konta)
        elif pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_stanje_konta)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Izveštaj o izvršenju budžeta možete da dobijete u okviru jedne kalendarske godine!",
                                   parent=self.prozor_stanje_konta)
        else:
            izvori = self.pronadji_ukupan_broj_izvora()
            self.__izabrana_kategorija(kategorija, pocetni, krajnji, izvori)

    def export_u_excel(self):
        podaci_za_excel = self.podaci_tabela.get()
        if podaci_za_excel == '':
            messagebox.showinfo("Greška", "Niste izabrali podatke!", parent=self.prozor_stanje_konta)
        else:
            df = pd.DataFrame(eval(podaci_za_excel))
            # df[1] = pd.to_numeric(df[1])
            for column in df.columns[1:]:
                # Ovde se pretvaraju None vrednosti iz baze u prazno, jer pandas ne moze da pretvori None u broj
                df[column] = pd.to_numeric(df[column], errors='coerce')

            # Ovde prazne vrednosti popunjava sa nulama
            df = df.fillna(0)
            try:
                df.to_excel('izvrsenje_budzeta.xlsx', float_format='%.2f', index=False, header=False)
                os.startfile('izvrsenje_budzeta.xlsx')
            except OSError:
                messagebox.showinfo("Upozorenje", "Morate zatvoriti prethodno otvoren excel dokument!", parent=self.prozor_stanje_konta)

    def __init__(self, master):
        self.master = master
        self.prozor_stanje_konta = Toplevel(self.master)
        self.prozor_stanje_konta.title("IZVEŠTAJI - Izvršenje budžeta")
        self.prozor_stanje_konta.resizable(False, False)
        self.prozor_stanje_konta.grab_set()
        # window_width = self.master.winfo_screenwidth() - 800
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        '''
        if self.master.winfo_screenwidth() < 1400:
            window_width = self.master.winfo_screenwidth() - 200
        else:
            window_width = self.master.winfo_screenwidth() - 800

        if self.master.winfo_screenheight() < 800:
            window_height = self.master.winfo_screenheight() - 200
        else:
            window_height = self.master.winfo_screenheight() - 420
        '''
        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_dnevnik_izvrsenje()
        window_height = dimenzije.odredi_visinu_izvrsenje()

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
        self.podaci_tabela = StringVar()
        self.tree_tabela_izvrsenje = None
        self.treeScroll = None

        # Prvi frame za unos podataka koji su potrebni za formiranje tabele
        self.prvi_frame = Frame(self.prozor_stanje_konta)
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=(2, 10), sticky='nsew')
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
        self.kategorija_combo['values'] = ('Klasa', 'Kategorija', 'Grupa', 'Sintetika', 'Analitika', 'Subanalitika')
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
        self.canvas_tabela_izvrsenje = Canvas(self.drugi_frame)
        self.canvas_tabela_izvrsenje.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_izvrsenje.columnconfigure(0, weight=1)
        self.canvas_tabela_izvrsenje.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25, fieldbackground="d3d3d3")
        # Boja selektrovanog reda

        self.style.map('Treeview', background=[('selected', '#347083')])

        koliko_ima_izvora = self.pronadji_ukupan_broj_izvora()
        self.prikazi_tabelu(koliko_ima_izvora)

        # Treci frame dugme za export u excel
        self.dugme_za_export = Button(self.prozor_stanje_konta, text="Eksport u excel", bg="#265073", fg="white", command=self.export_u_excel)
        self.dugme_za_export.grid(row=2, column=0)
