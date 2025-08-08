from tkinter import Toplevel, LabelFrame, Frame, Canvas, ttk, Label, Button, messagebox
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
import locale
import tkinter as tk
import xlsxwriter
import os


# Polje sa dugmadima za izvestaje
class PlaceniAvansi:

    # Ova funkcija kovertuje rezultat iz baze tako sto vrednosti None kovertuje u nulu
    def __konvertuj_none_nula(self, niz):
        rezultat = []
        for record in niz:
            konvertovano = [0 if v is None else v for v in record]
            rezultat.append(konvertovano)

        return rezultat

    # Pomocna funkcija za prikaz podataka u tabeli
    def __prikaz_podataka_u_tabeli(self, rezultat_stavke):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog

        # Ovo mora u slucaju da izabrani period za zakljucni list nema podataka, pa da se izbegne prijava greske
        if rezultat_stavke is not None:
            self.tree_tabela_placeni_avansi.delete(*self.tree_tabela_placeni_avansi.get_children())
            # Pretraga baze za stavkama naloga
            # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli

            self.tree_tabela_placeni_avansi.tag_configure('oddrow', background="white")
            self.tree_tabela_placeni_avansi.tag_configure('evenrow', background="lightblue")
            # self.podaci_tabela.set(rezultat_stavke)
            count_stavke_naloga = 0
            konvertovan_rezultat = self.__konvertuj_none_nula(rezultat_stavke)
            '''
            konvertovan_rezultat = []
            for record in rezultat_stavke:
                konvertovano = [0 if v is None else v for v in record]
                konvertovan_rezultat.append(konvertovano)
            '''
            for record in konvertovan_rezultat:
                ukupno_dug = record[1]+record[3]
                ukupno_potr = record[2]+record[4]
                ukupan_saldo = ukupno_dug-ukupno_potr
                if ukupan_saldo > 0:
                    saldo_dug = ukupan_saldo
                    saldo_pot = 0
                elif ukupan_saldo < 0:
                    saldo_dug = 0
                    saldo_pot = abs(ukupan_saldo)
                else:
                    saldo_dug = 0
                    saldo_pot = 0

                pocetno_duguje = locale.format_string('%10.2f', record[1], grouping=True)
                pocetno_potrazuje = locale.format_string('%10.2f', record[2], grouping=True)
                tekuce_duguje = locale.format_string('%10.2f', record[3], grouping=True)
                tekuce_potrazuje = locale.format_string('%10.2f', record[4], grouping=True)
                ukupno_duguje = locale.format_string('%10.2f', ukupno_dug, grouping=True)
                ukupno_potrazuje = locale.format_string('%10.2f', ukupno_potr, grouping=True)
                saldo_duguje = locale.format_string('%10.2f', saldo_dug, grouping=True)
                saldo_potrazuje = locale.format_string('%10.2f', saldo_pot, grouping=True)

                if count_stavke_naloga % 2 == 0:
                    self.tree_tabela_placeni_avansi.insert(parent='', index='end', iid=count_stavke_naloga, text='',
                                                   values=(record[0], pocetno_duguje, pocetno_potrazuje, tekuce_duguje, tekuce_potrazuje, ukupno_duguje, ukupno_potrazuje, saldo_duguje, saldo_potrazuje),
                                                   tags=('evenrow',))
                else:
                    self.tree_tabela_placeni_avansi.insert(parent='', index='end', iid=count_stavke_naloga, text='',
                                                   values=(record[0], pocetno_duguje, pocetno_potrazuje, tekuce_duguje, tekuce_potrazuje, ukupno_duguje, ukupno_potrazuje, saldo_duguje, saldo_potrazuje),
                                                   tags=('oddrow',))
                count_stavke_naloga += 1

    def __izvuci_placene_avanse(self, pocetni_datum, krajnji_datum):
        # godina = pocetni_datum.year
        # rezultat = []
        konto_conn = KontoController()
        rezultat = konto_conn.knjiga_placeni_avansi(pocetni_datum, krajnji_datum)
        return rezultat

    # Prikaz zakljucnog lista
    def prikazi(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year

        if pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_placeni_avansi)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Pomoćnu knjigu plaćenih avansa možete da dobijete u okviru jedne kalendarske godine!", parent=self.prozor_placeni_avansi)
        else:
            podaci = self.__izvuci_placene_avanse(pocetni, krajnji)
            self.__prikaz_podataka_u_tabeli(podaci)

    def pravljenje_excel_izvestaja(self, podaci, pocetni, krajnji):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('pomocna_knjiga_avansa_excel.xlsx')
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        zaglavlje_naslov = workbook.add_format({'valign': 'center', 'bold': True})
        zaglavlje = workbook.add_format({'valign': 'center', 'bold': True, 'bg_color': '#99c7f7'})
        # Add a number format for cells
        money = workbook.add_format({'num_format': '#,##0.00'})
        naslovni_titl = 'PLAĆENI AVANSI OD ' + pocetni.strftime("%d.%m.%Y.") + ' - ' + krajnji.strftime("%d.%m.%Y.")
        bold_money = workbook.add_format({'num_format': '#,##0.00', 'bold': True})
        # format_datuma = workbook.add_format({'num_format': 'dd.mm.yyyy.'})
        worksheet.merge_range(0, 0, 0, 8, naslovni_titl, zaglavlje_naslov)
        # Write some data headers.
        worksheet.write(1, 0, '', zaglavlje)
        # worksheet.write(1, 1, '', zaglavlje_naslov)
        worksheet.merge_range(1, 1, 1, 2, 'Početno', zaglavlje)
        worksheet.merge_range(1, 3, 1, 4, 'Tekuće', zaglavlje)
        worksheet.merge_range(1, 5, 1, 6, 'Ukupno', zaglavlje)
        worksheet.merge_range(1, 7, 1, 8, 'Saldo', zaglavlje)
        worksheet.write('A3', 'Naziv', zaglavlje)
        worksheet.write('B3', 'Duguje', zaglavlje)
        worksheet.write('C3', 'Potražuje', zaglavlje)
        worksheet.write('D3', 'Duguje', zaglavlje)
        worksheet.write('E3', 'Potražuje', zaglavlje)
        worksheet.write('F3', 'Duguje', zaglavlje)
        worksheet.write('G3', 'Potražuje', zaglavlje)
        worksheet.write('H3', 'Duguje', zaglavlje)
        worksheet.write('I3', 'Potražuje', zaglavlje)

        # Start from the first cell below the headers.
        row = 3
        col = 0

        # Iterate over the data and write it out row by row.
        for naziv, pocetno_duguje, pocetno_potrazuje, tekuce_duguje, tekuce_potrazuje in podaci:
            ukupno_duguje = pocetno_duguje+tekuce_duguje
            ukupno_potrazuje = pocetno_potrazuje+tekuce_potrazuje
            ukupan_saldo = ukupno_duguje-ukupno_potrazuje
            if ukupan_saldo > 0:
                saldo_dug = ukupan_saldo
                saldo_pot = 0
            elif ukupan_saldo < 0:
                saldo_dug = 0
                saldo_pot = abs(ukupan_saldo)
            else:
                saldo_dug = 0
                saldo_pot = 0
            worksheet.write(row, col, naziv)
            worksheet.write(row, col + 1, pocetno_duguje, money)
            worksheet.write(row, col + 2, pocetno_potrazuje, money)
            worksheet.write(row, col + 3, tekuce_duguje, money)
            worksheet.write(row, col + 4, tekuce_potrazuje, money)
            worksheet.write(row, col + 5, ukupno_duguje, money)
            worksheet.write(row, col + 6, ukupno_potrazuje, money)
            worksheet.write(row, col + 7, saldo_dug, money)
            worksheet.write(row, col + 8, saldo_pot, money)
            row += 1

        # Write a total using a formula.
        # worksheet.write(row, 0, 'Total', bold)
        # worksheet.write(row, 1, '=SUM(B2:B5)', money)
        worksheet.autofit()
        workbook.close()
        os.startfile('pomocna_knjiga_avansa_excel.xlsx')

    def exportuj_placene_avanse(self):
        try:
            pocetni = self.datum_od.get_date()
            krajnji = self.datum_do.get_date()
            rezultat = self.__izvuci_placene_avanse(pocetni, krajnji)
            konvertovan_rezultat = self.__konvertuj_none_nula(rezultat)

            # Eksportovati novi_niz u excel
            self.pravljenje_excel_izvestaja(konvertovan_rezultat, pocetni, krajnji)
        except:
            messagebox.showwarning("Greška", "Morate zatvoriti prethodni excel izveštaj!", parent=self.prozor_placeni_avansi)

    def __init__(self, master):
        self.master = master
        self.prozor_placeni_avansi = Toplevel(self.master)
        self.prozor_placeni_avansi.title("IZVEŠTAJI - Pomoćna knjiga plaćenih avansa")
        self.prozor_placeni_avansi.resizable(False, False)
        self.prozor_placeni_avansi.grab_set()
        # window_width = self.master.winfo_screenwidth() - 400
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_zakljucni_list()
        window_height = dimenzije.odredi_visinu_zakljucni_list()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_placeni_avansi.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_placeni_avansi.columnconfigure(0, weight=1)
        self.prozor_placeni_avansi.rowconfigure(0, weight=1)
        self.prozor_placeni_avansi.rowconfigure(1, weight=6)
        self.prozor_placeni_avansi.rowconfigure(2, weight=1)

        # Prvi frame za unos podataka koji su potrebni za formiranje tabele
        self.prvi_frame = Frame(self.prozor_placeni_avansi)
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
        self.drugi_frame = Frame(self.prozor_placeni_avansi)
        self.drugi_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.drugi_frame.columnconfigure(0, weight=1)
        self.drugi_frame.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_tabela_placeni_avansi = Canvas(self.drugi_frame)
        self.canvas_tabela_placeni_avansi.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_placeni_avansi.columnconfigure(0, weight=1)
        self.canvas_tabela_placeni_avansi.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25, fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])
        self.tree_tabela_placeni_avansi = ttk.Treeview(self.canvas_tabela_placeni_avansi)
        self.tree_tabela_placeni_avansi.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.tree_tabela_placeni_avansi['columns'] = ("Naziv", "Početno duguje", "Početno potražuje", "Tekuće duguje", "Tekuće potražuje", "Ukupno duguje", "Ukupno potražuje", "Saldo duguje", "Saldo potražuje")
        self.tree_tabela_placeni_avansi.column("#0", width=0, stretch=False)
        self.tree_tabela_placeni_avansi.column("Naziv", anchor=tk.W, width=200)
        self.tree_tabela_placeni_avansi.column("Početno duguje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Početno potražuje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Tekuće duguje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Tekuće potražuje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Ukupno duguje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Ukupno potražuje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Saldo duguje", anchor=tk.E, width=100)
        self.tree_tabela_placeni_avansi.column("Saldo potražuje", anchor=tk.E, width=100)
        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_placeni_avansi)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_placeni_avansi.yview)
        self.tree_tabela_placeni_avansi.configure(yscrollcommand=self.treeScroll.set)

        self.tree_tabela_placeni_avansi.heading("#0", anchor=tk.W, text="")
        self.tree_tabela_placeni_avansi.heading("Naziv", anchor=tk.CENTER, text="Naziv")
        self.tree_tabela_placeni_avansi.heading("Početno duguje", anchor=tk.CENTER, text="Početno duguje")
        self.tree_tabela_placeni_avansi.heading("Početno potražuje", anchor=tk.CENTER, text="Početno potražuje")
        self.tree_tabela_placeni_avansi.heading("Tekuće duguje", anchor=tk.CENTER, text="Tekuće duguje")
        self.tree_tabela_placeni_avansi.heading("Tekuće potražuje", anchor=tk.CENTER, text="Tekuće potražuje")
        self.tree_tabela_placeni_avansi.heading("Ukupno duguje", anchor=tk.CENTER, text="Ukupno duguje")
        self.tree_tabela_placeni_avansi.heading("Ukupno potražuje", anchor=tk.CENTER, text="Ukupno potražuje")
        self.tree_tabela_placeni_avansi.heading("Saldo duguje", anchor=tk.CENTER, text="Saldo duguje")
        self.tree_tabela_placeni_avansi.heading("Saldo potražuje", anchor=tk.CENTER, text="Saldo potražuje")
        # Treci frame dugme za štampu
        self.dugme_za_stampu = Button(self.prozor_placeni_avansi, text="Eksport u excel", bg="#265073", fg="white", command=self.exportuj_placene_avanse)
        self.dugme_za_stampu.grid(row=2, column=0)
