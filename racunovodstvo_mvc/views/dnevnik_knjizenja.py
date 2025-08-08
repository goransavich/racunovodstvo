from tkinter import Toplevel, LabelFrame, Frame, Canvas, ttk, Label, Button, messagebox
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.NaloziController import NaloziController
from racunovodstvo_mvc.views.stampa_izvestaja import StampaIzvestaja
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
import locale
import tkinter as tk
import xlsxwriter
import os
import decimal


class DnevnikKnjizenja:
    # Ogranicenje duzine teksta
    def __broj_karaktera(self, tekst: str, duzina: int):
        return tekst[:duzina]

    # Dobijanje podataka za dnevnik knjizenja iz baze
    def __izvuci_dnevnik_knjizenja(self, pocetni_datum, krajnji_datum):
        nalog_conn = NaloziController()
        rezultat = nalog_conn.read_dnevnik_knjizenja(pocetni_datum, krajnji_datum)
        return rezultat

    # Provera da li u izabranom periodu ima podataka, ako nema bila bi greska u konzoli, pa se ovim to ispravlja
    def __proveri_da_li_je_prazan_dnevnik(self, rezultat):
        # Ova provera mora u slucaju da za izabrani period nema podataka, da ne bi prijavljivao gresku u dataframe
        if len(rezultat) == 0:
            self.tree_tabela_dnevnik_knjizenja.delete(*self.tree_tabela_dnevnik_knjizenja.get_children())
            messagebox.showwarning("Obaveštenje", "Nema podataka za izabrani period!", parent=self.prozor_dnevnik_knjizenja)
            return None

    # Pomocna funkcija za odredjivanje gde ce u tabeli biti prikazan iznos duguje ili potrazuje
    def duguje_potrazuje_even(self, id_sloga, prvi_deo, drugi_deo, treci_deo, cetvrti_deo, peti_deo, sesti_deo, sedmi_deo):
        oznaka_konta = self.__broj_karaktera(cetvrti_deo, 19)
        naziv_konta = self.__broj_karaktera(peti_deo, 50)
        if sedmi_deo == 'd':
            self.tree_tabela_dnevnik_knjizenja.insert(parent='', index='end', iid=id_sloga, text='',
                                          values=(prvi_deo, drugi_deo.strftime("%d.%m.%Y"), treci_deo, oznaka_konta, naziv_konta, sesti_deo, ''),
                                          tags=('evenrow',))
        else:
            self.tree_tabela_dnevnik_knjizenja.insert(parent='', index='end', iid=id_sloga, text='',
                                          values=(prvi_deo, drugi_deo.strftime("%d.%m.%Y"), treci_deo, oznaka_konta, naziv_konta, '', sesti_deo),
                                          tags=('evenrow',))

    # Pomocna funkcija za odredjivanje gde ce u tabeli biti prikazan iznos duguje ili potrazuje
    def duguje_potrazuje_odd(self, id_sloga, prvi_deo, drugi_deo, treci_deo, cetvrti_deo, peti_deo, sesti_deo, sedmi_deo):
        oznaka_konta = self.__broj_karaktera(cetvrti_deo, 19)
        naziv_konta = self.__broj_karaktera(peti_deo, 50)
        if sedmi_deo == 'd':
            self.tree_tabela_dnevnik_knjizenja.insert(parent='', index='end', iid=id_sloga, text='', values=(prvi_deo, drugi_deo.strftime("%d.%m.%Y"), treci_deo, oznaka_konta, naziv_konta, sesti_deo, ''), tags=('oddrow',))
        else:
            self.tree_tabela_dnevnik_knjizenja.insert(parent='', index='end', iid=id_sloga, text='', values=(prvi_deo, drugi_deo.strftime("%d.%m.%Y"), treci_deo, oznaka_konta, naziv_konta, '', sesti_deo), tags=('oddrow',))

    # Pomocna funkcija za prikaz podataka u tabeli
    def __prikaz_podataka_u_tabeli(self, rezultat_stavke):
        # Brisanje entry polja nakon azuriranja konta
        locale.setlocale(locale.LC_ALL, 'de_DE')

        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog
        self.tree_tabela_dnevnik_knjizenja.delete(*self.tree_tabela_dnevnik_knjizenja.get_children())
        # Pretraga baze za stavkama naloga
        # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli

        self.tree_tabela_dnevnik_knjizenja.tag_configure('oddrow', background="white")
        self.tree_tabela_dnevnik_knjizenja.tag_configure('evenrow', background="lightblue")

        count_stavke_naloga = 0

        for record in rezultat_stavke:

            iznos_za_prikaz = locale.format_string('%10.2f', record[5], grouping=True)

            # Prikaz u tabeli
            if count_stavke_naloga % 2 == 0:
                self.duguje_potrazuje_even(count_stavke_naloga, record[0], record[1], record[2], record[3], record[4], iznos_za_prikaz, record[6])
            else:
                self.duguje_potrazuje_odd(count_stavke_naloga, record[0], record[1], record[2], record[3], record[4], iznos_za_prikaz, record[6])

            count_stavke_naloga += 1

    # Prikaz dnevnika knjizenja
    def prikazi(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year

        if pocetni > krajnji:
            messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!",
                                   parent=self.prozor_dnevnik_knjizenja)
        elif pocetna_godina != krajnja_godina:
            messagebox.showwarning("Greška", "Dnevnik knjiženja možete da dobijete u okviru jedne kalendarske godine!",
                                   parent=self.prozor_dnevnik_knjizenja)
        else:
            podaci = self.__izvuci_dnevnik_knjizenja(pocetni, krajnji)
            self.__proveri_da_li_je_prazan_dnevnik(podaci)
            self.__prikaz_podataka_u_tabeli(podaci)

    def stampaj_dnevnik(self):
        try:
            pocetni = self.datum_od.get_date()
            krajnji = self.datum_do.get_date()
            stampanje = StampaIzvestaja()
            stampanje.stampa_dnevnik(self.__izvuci_dnevnik_knjizenja(pocetni, krajnji), pocetni, krajnji)
        except OSError:
            messagebox.showwarning("Greška", "Morate zatvoriti prethodni PDF izveštaj!", parent=self.prozor_dnevnik_knjizenja)

    def pravljenje_excel_izvestaja(self, podaci):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('dnevnik_knjizenja_excel.xlsx')
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})
        naslov = workbook.add_format({'valign': 'center', 'bold': True})
        zaglavlje_naslov = workbook.add_format({'valign': 'center', 'bold': True, 'bg_color': '#99c7f7'})
        # Add a number format for cells
        money = workbook.add_format({'num_format': '#,##0.00'})

        bold_money = workbook.add_format({'num_format': '#,##0.00', 'bold': True})
        format_datuma = workbook.add_format({'num_format': 'dd.mm.yyyy.'})

        # Write some data headers.
        worksheet.merge_range(0, 0, 0, 6, 'DNEVNIK KNJIŽENJA', naslov)
        worksheet.write('A2', 'Broj naloga', zaglavlje_naslov)
        worksheet.write('B2', 'Datum naloga', zaglavlje_naslov)
        worksheet.write('C2', 'Vrsta naloga', zaglavlje_naslov)
        worksheet.write('D2', 'Konto', zaglavlje_naslov)
        worksheet.write('E2', 'Naziv ekonomske klasifikacije', zaglavlje_naslov)
        worksheet.write('F2', 'Duguje', zaglavlje_naslov)
        worksheet.write('G2', 'Potrazuje', zaglavlje_naslov)

        # Start from the first cell below the headers.
        row = 2
        col = 0
        broj_naloga = ""
        duguje_total = 0
        potrazuje_total = 0
        # Iterate over the data and write it out row by row.
        for broj, datum, vrsta, konto, naziv, duguje, potrazuje in podaci:
            # Ovde ide provera jer polja duguje i potrazuje kada su prazna imaju tip string, a on ne moze da se sabira
            if duguje == "":
                duguje = decimal.Decimal(0.00)
            if potrazuje == "":
                potrazuje = decimal.Decimal(0.00)

            # Ovde se pravi subtotal po nalogu
            if broj_naloga == "":
                # duguje_total += duguje
                # potrazuje_total += potrazuje
                broj_naloga = broj

            if broj != broj_naloga:
                worksheet.write(row, col + 4, 'Ukupno za nalog:', bold)
                worksheet.write(row, col + 5, duguje_total, bold_money)
                worksheet.write(row, col + 6, potrazuje_total, bold_money)
                duguje_total = 0
                potrazuje_total = 0
                duguje_total += duguje
                potrazuje_total += potrazuje
                row += 1
                broj_naloga = broj
            else:
                duguje_total += duguje
                potrazuje_total += potrazuje
                broj_naloga = broj

            worksheet.write(row, col, broj)
            worksheet.write(row, col + 1, datum, format_datuma)
            worksheet.write(row, col + 2, vrsta)
            worksheet.write(row, col + 3, konto)
            worksheet.write(row, col + 4, naziv)
            worksheet.write(row, col + 5, duguje, money)
            worksheet.write(row, col + 6, potrazuje, money)
            row += 1

        # Ovde unosim vrednosti totala za poslednji nalog u nizu
        worksheet.write(row, col + 4, 'Ukupno za nalog:', bold)
        worksheet.write(row, col + 5, duguje_total, bold_money)
        worksheet.write(row, col + 6, potrazuje_total, bold_money)

        # Write a total using a formula.
        # worksheet.write(row, 0, 'Total', bold)
        # worksheet.write(row, 1, '=SUM(B2:B5)', money)
        worksheet.autofit()
        workbook.close()
        os.startfile('dnevnik_knjizenja_excel.xlsx')

    def eksportovanje(self):
        try:
            pocetni = self.datum_od.get_date()
            krajnji = self.datum_do.get_date()
            rezultat = self.__izvuci_dnevnik_knjizenja(pocetni, krajnji)
            novi_niz = []
            for record in rezultat:
                nova_lista = list(record)
                iznos = nova_lista[5]
                if nova_lista[6] == 'd':
                    nova_lista[6] = ''
                else:
                    nova_lista[5] = ''
                    nova_lista[6] = iznos
                novi_tuple = tuple(nova_lista)
                novi_niz.append(novi_tuple)

            # Eksportovati novi_niz u excel
            # print(novi_niz)
            self.pravljenje_excel_izvestaja(novi_niz)
        except:
            messagebox.showwarning("Greška", "Morate zatvoriti prethodni excel dokument!", parent=self.prozor_dnevnik_knjizenja)

    def __init__(self, master):
        self.master = master
        self.prozor_dnevnik_knjizenja = Toplevel(self.master)
        self.prozor_dnevnik_knjizenja.title("IZVEŠTAJI - Dnevnik knjiženja")
        self.prozor_dnevnik_knjizenja.resizable(False, False)
        self.prozor_dnevnik_knjizenja.grab_set()
        # window_width = self.master.winfo_screenwidth() - 600
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_dnevnik_izvrsenje()
        window_height = dimenzije.odredi_visinu_dnevnik()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_dnevnik_knjizenja.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_dnevnik_knjizenja.columnconfigure(0, weight=1)
        self.prozor_dnevnik_knjizenja.rowconfigure(0, weight=1)
        self.prozor_dnevnik_knjizenja.rowconfigure(1, weight=6)
        self.prozor_dnevnik_knjizenja.rowconfigure(2, weight=1)

        # Prvi frame za unos podataka koji su potrebni za formiranje tabele
        self.prvi_frame = Frame(self.prozor_dnevnik_knjizenja)
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
        self.datum_od = DateEntry(self.izbor_datuma, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy',
                                  font="8")
        self.datum_od.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.izbor_datuma, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy',
                                  font="8")
        self.datum_do.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Dugme za pokretanje trazenja
        self.pretrazi = Button(self.izbor_datuma, text="Prikaži", command=self.prikazi)
        self.pretrazi.grid(row=1, column=5, padx=10, pady=10, sticky='ew')

        ##########################################################################################
        # Drugi frame - tabela
        self.drugi_frame = Frame(self.prozor_dnevnik_knjizenja)
        self.drugi_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.drugi_frame.columnconfigure(0, weight=1)
        self.drugi_frame.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_tabela_dnevnik_knjizenja = Canvas(self.drugi_frame)
        self.canvas_tabela_dnevnik_knjizenja.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_dnevnik_knjizenja.columnconfigure(0, weight=1)
        self.canvas_tabela_dnevnik_knjizenja.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                             fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])
        self.tree_tabela_dnevnik_knjizenja = ttk.Treeview(self.canvas_tabela_dnevnik_knjizenja)
        self.tree_tabela_dnevnik_knjizenja.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.tree_tabela_dnevnik_knjizenja['columns'] = ("Broj naloga", "Datum naloga", "Vrsta naloga", "Konto", "Naziv konta", "Duguje", "Potrazuje")
        self.tree_tabela_dnevnik_knjizenja.column("#0", width=0, stretch=False)
        self.tree_tabela_dnevnik_knjizenja.column("Broj naloga", anchor=tk.CENTER, width=80)
        self.tree_tabela_dnevnik_knjizenja.column("Vrsta naloga", anchor=tk.CENTER, width=100)
        self.tree_tabela_dnevnik_knjizenja.column("Datum naloga", anchor=tk.CENTER, width=80)
        self.tree_tabela_dnevnik_knjizenja.column("Konto", anchor=tk.W, width=100)
        self.tree_tabela_dnevnik_knjizenja.column("Naziv konta", anchor=tk.W, width=300)
        self.tree_tabela_dnevnik_knjizenja.column("Duguje", anchor=tk.E, width=100)
        self.tree_tabela_dnevnik_knjizenja.column("Potrazuje", anchor=tk.E, width=100)
        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_dnevnik_knjizenja)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_dnevnik_knjizenja.yview)
        self.tree_tabela_dnevnik_knjizenja.configure(yscrollcommand=self.treeScroll.set)

        self.tree_tabela_dnevnik_knjizenja.heading("#0", anchor=tk.W, text="")
        self.tree_tabela_dnevnik_knjizenja.heading("Broj naloga", anchor=tk.CENTER, text="Broj naloga")
        self.tree_tabela_dnevnik_knjizenja.heading("Vrsta naloga", anchor=tk.CENTER, text="Vrsta naloga")
        self.tree_tabela_dnevnik_knjizenja.heading("Datum naloga", anchor=tk.CENTER, text="Datum naloga")
        self.tree_tabela_dnevnik_knjizenja.heading("Konto", anchor=tk.CENTER, text="Konto")
        self.tree_tabela_dnevnik_knjizenja.heading("Naziv konta", anchor=tk.CENTER, text="Naziv konta")
        self.tree_tabela_dnevnik_knjizenja.heading("Duguje", anchor=tk.CENTER, text="Duguje")
        self.tree_tabela_dnevnik_knjizenja.heading("Potrazuje", anchor=tk.CENTER, text="Potrazuje")

        # Treci frame dugme za štampu
        self.treci_frame = Frame(self.prozor_dnevnik_knjizenja)
        self.treci_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.treci_frame.columnconfigure(0, weight=1)
        self.treci_frame.columnconfigure(1, weight=1)
        self.treci_frame.columnconfigure(2, weight=1)
        self.treci_frame.columnconfigure(3, weight=1)
        self.treci_frame.columnconfigure(4, weight=1)
        self.treci_frame.columnconfigure(5, weight=1)
        self.dugme_za_stampu = Button(self.treci_frame, text="Štampa", bg="#265073", fg="white",
                                      command=self.stampaj_dnevnik)
        self.dugme_za_stampu.grid(row=0, column=2, padx=10, pady=10, sticky='ew')
        self.excel = Button(self.treci_frame, text="Eksport u excel", bg="#265073", fg="white",
                            command=self.eksportovanje)
        self.excel.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
