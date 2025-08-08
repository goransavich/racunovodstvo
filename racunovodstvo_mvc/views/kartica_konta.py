from tkinter import Toplevel, LabelFrame, Frame, Canvas, ttk, Label, Button, messagebox, StringVar
from tkcalendar import DateEntry
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.NaloziController import NaloziController
from racunovodstvo_mvc.views.stampa_izvestaja import StampaIzvestaja
from racunovodstvo_mvc.views.nalozi import Nalozi
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
import locale
import tkinter as tk


class KarticaKonta:
    # Da se ne bi u tabeli prikazivali None ako nema broja, ova funkcija vraca 0.00
    def __is_number_none(self, broj):
        if broj is None:
            return float(0)
        else:
            return broj

    # Smanjivanje liste konta u comboboxu na osnovu onoga sto kuca korisnik
    def __check_input(self, event):
        value = event.widget.get()
        if value == '':
            self.konto_combo['values'] = self.konta_subanalitika_lista
        else:
            data = []
            for item in self.konta_subanalitika_lista:
                if value.lower() in item.lower():
                    data.append(item)

            self.konto_combo['values'] = data

    # Pomocna metoda za dobijanje liste subanalitickih konta iz baze podataka
    def __lista_subanalitickih_konta(self):
        # Uzimanje iz baze spisak konta subanalitike
        try:
            conn = KontoController()
            konta_subanalitika = conn.read_condition()
            konta_lista = []
            for i in konta_subanalitika:
                konta_lista.append(i[1])
            return konta_lista
        except ValueError:
            messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom čitanja konta iz baze!!",
                                   parent=self.prozor_kartica_konta)

    # Pomocna funkcija za odredjivanje gde ce u tabeli biti prikazan iznos duguje ili potrazuje
    def duguje_potrazuje_even(self, id_sloga, prvi_deo, drugi_deo, treci_deo, cetvrti_deo):
        if cetvrti_deo == 'd':
            self.tree_tabela_kartica.insert(parent='', index='end', iid=id_sloga, text='', values=(prvi_deo, drugi_deo, treci_deo, ''), tags=('evenrow',))
        else:
            self.tree_tabela_kartica.insert(parent='', index='end', iid=id_sloga, text='', values=(prvi_deo, drugi_deo, '', treci_deo), tags=('evenrow',))

    # Pomocna funkcija za odredjivanje gde ce u tabeli biti prikazan iznos duguje ili potrazuje
    def duguje_potrazuje_odd(self, redni_broj, prvi_deo, drugi_deo, treci_deo, cetvrti_deo):
        if cetvrti_deo == 'd':
            self.tree_tabela_kartica.insert(parent='', index='end', iid=redni_broj, text='', values=(prvi_deo, drugi_deo, treci_deo, ''), tags=('oddrow',))
        else:
            self.tree_tabela_kartica.insert(parent='', index='end', iid=redni_broj, text='', values=(prvi_deo, drugi_deo, '', treci_deo), tags=('oddrow',))

    # Pomocna funkcija za prikaz podataka u tabeli
    def __prikaz_podataka_u_tabeli(self, rezultat_stavke):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog
        self.tree_tabela_kartica.delete(*self.tree_tabela_kartica.get_children())
        # Pretraga baze za stavkama naloga
        # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli
        self.tree_tabela_kartica.tag_configure('oddrow', background="white")
        self.tree_tabela_kartica.tag_configure('evenrow', background="lightblue")
        count_stavke = 0
        duguje = 0
        potrazuje = 0
        for record in rezultat_stavke:
            # Racunanje salda naloga duguje/potrazuje
            if record[4] == 'd':
                duguje += record[3]
            else:
                potrazuje += record[3]

            iznos = locale.format_string('%10.2f', self.__is_number_none(record[3]), grouping=True)
            # Prikaz u tabeli
            if count_stavke % 2 == 0:
                self.duguje_potrazuje_even(count_stavke, record[1], record[2].strftime("%d.%m.%Y"), iznos, record[4])
            else:
                self.duguje_potrazuje_odd(count_stavke, record[1], record[2].strftime("%d.%m.%Y"), iznos, record[4])

            count_stavke += 1

        saldo = duguje-potrazuje
        duguje_prikaz = locale.format_string('%10.2f', duguje, grouping=True)
        potrazuje_prikaz = locale.format_string('%10.2f', potrazuje, grouping=True)
        saldo_prikaz = locale.format_string('%10.2f', saldo, grouping=True)
        # Racunanje ukupno za nalog duguje ili potrazuje
        self.saldo_unos_duguje.config(text=duguje_prikaz)
        self.saldo_unos_potrazuje.config(text=potrazuje_prikaz)
        self.saldo_ukupno.config(text=saldo_prikaz)

    def __pronadji_karticu(self, konto, pocetni, krajnji):
        conn_kartica = KontoController()
        return conn_kartica.kartica_konta(konto, pocetni, krajnji)

    # Dobijanje ID konta
    def __pronadji_id_konta(self, konto_oznaka):
        conn_konto = KontoController()
        pronadji_konto = conn_konto.find(konto_oznaka)
        return pronadji_konto[0][0]

    def prikazi(self):
        pocetni = self.datum_od.get_date()
        krajnji = self.datum_do.get_date()
        pocetna_godina = pocetni.year
        krajnja_godina = krajnji.year
        konto_oznaka = self.konto_combo.get()
        if konto_oznaka in self.konta_subanalitika_lista:
            # Dobijanje ID konta
            konto = self.__pronadji_id_konta(konto_oznaka)
            if konto == "":
                messagebox.showwarning("Greška", "Niste izabrali konto!", parent=self.prozor_kartica_konta)
            elif pocetni > krajnji:
                messagebox.showwarning("Greška", "Početni datum je veći od završnog datuma!", parent=self.prozor_kartica_konta)
            elif pocetna_godina != krajnja_godina:
                messagebox.showwarning("Greška", "Karticu konta možete da dobijete u okviru jedne kalendarske godine!",
                                       parent=self.prozor_kartica_konta)
            else:
                # Setovanje promenjive oznaka_konta da bih mogao da prikazem konto na izvestaju
                self.oznaka_konta.set(konto_oznaka)
                self.rezultat_kartice_konta = self.__pronadji_karticu(konto, pocetni, krajnji)
                self.__prikaz_podataka_u_tabeli(self.rezultat_kartice_konta)
        else:
            messagebox.showwarning("Greška", "Morate izabrati konto iz padajuće liste!", parent=self.prozor_kartica_konta)

    # Kada se selektuje red može da se ovori nalog da se vide detalji
    def pregledaj_nalog(self):
        # Pronalazenje ID naloga na osnovu klika
        selected = self.tree_tabela_kartica.focus()

        # Pronadji nalog po ID-u
        if selected:
            id_naloga = self.rezultat_kartice_konta[int(selected)][0]
            conn_pronadji = NaloziController()
            pronadjen_nalog = conn_pronadji.find_nalog(id_naloga)
            # Otvaranje prozora naloga
            conn_nalozi = Nalozi(self.prozor_kartica_konta)
            conn_nalozi.kreiran_nalog(pronadjen_nalog[0][0], pronadjen_nalog[0][1].strftime("%d.%m.%Y"), pronadjen_nalog[0][2], pronadjen_nalog[0][3])
        else:
            messagebox.showwarning("Greška", "Hmmmmm, niste selektovali red!", parent=self.prozor_kartica_konta)

    def stampaj_karticu(self):
        try:
            oznaka_konta_izvestaj = self.oznaka_konta.get()
            stampanje = StampaIzvestaja()
            stampanje.stampa_kartice_konta(self.rezultat_kartice_konta, oznaka_konta_izvestaj)
        except OSError:
            messagebox.showwarning("Greška", "Morate zatvoriti prethodni PDF izveštaj!", parent=self.prozor_kartica_konta)

    def __init__(self, master):
        self.master = master
        self.prozor_kartica_konta = Toplevel()
        self.prozor_kartica_konta.title("IZVEŠTAJI - Kartica konta")
        self.prozor_kartica_konta.resizable(False, False)
        self.prozor_kartica_konta.grab_set()
        # window_width = self.master.winfo_screenwidth() - 800
        # window_height = self.master.winfo_screenheight() - 420
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        '''
        if self.master.winfo_screenwidth() < 1400:
            window_width = self.master.winfo_screenwidth() - 300
        else:
            window_width = self.master.winfo_screenwidth() - 800

        if self.master.winfo_screenheight() < 800:
            window_height = self.master.winfo_screenheight() - 180
        else:
            window_height = self.master.winfo_screenheight() - 420
        '''
        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_kartica_konta_stanje()
        window_height = dimenzije.odredi_visinu_kartica_konta_stanje()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_kartica_konta.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_kartica_konta.columnconfigure(0, weight=1)
        self.prozor_kartica_konta.rowconfigure(0, weight=1)
        self.prozor_kartica_konta.rowconfigure(1, weight=4)
        self.prozor_kartica_konta.rowconfigure(2, weight=1)
        self.prozor_kartica_konta.rowconfigure(3, weight=1)
        # Prvi frame za unos podataka koji su potrebni za formiranje tabele
        self.prvi_frame = Frame(self.prozor_kartica_konta)
        self.prvi_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.prvi_frame.columnconfigure(0, weight=1)
        self.prvi_frame.rowconfigure(0, weight=1)
        self.stanje_kartica_konta = LabelFrame(self.prvi_frame, text="Pregled kartice konta", bg="lightblue")
        self.stanje_kartica_konta.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.stanje_kartica_konta.columnconfigure(0, weight=1)
        self.stanje_kartica_konta.columnconfigure(1, weight=1)
        self.stanje_kartica_konta.columnconfigure(2, weight=1)
        self.stanje_kartica_konta.columnconfigure(3, weight=1)
        self.stanje_kartica_konta.columnconfigure(4, weight=1)
        self.stanje_kartica_konta.columnconfigure(5, weight=1)
        self.stanje_kartica_konta.rowconfigure(0, weight=1)
        self.stanje_kartica_konta.rowconfigure(1, weight=1)
        self.oznaka_konta = StringVar()
        self.rezultat_kartice_konta = ()
        # Label tekst
        self.izaberi_konto_text = Label(self.stanje_kartica_konta, text="Izaberi konto:", bg="lightblue")
        self.izaberi_konto_text.grid(row=0, column=0, padx=10, sticky="w")
        # Label Datum od
        self.datum_od_text = Label(self.stanje_kartica_konta, text="Datum od:", bg="lightblue")
        self.datum_od_text.grid(row=0, column=1, padx=10, sticky="w")
        # Label Datum do
        self.datum_do_text = Label(self.stanje_kartica_konta, text="Datum do:", bg="lightblue")
        self.datum_do_text.grid(row=0, column=3, padx=10, sticky="w")
        # Combobox za izbor vrste naloga
        self.konta_subanalitika_lista = self.__lista_subanalitickih_konta()
        self.konto_combo = ttk.Combobox(self.stanje_kartica_konta, font="8", background="lightblue", values=self.konta_subanalitika_lista)
        self.konto_combo.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.konto_combo.bind("<KeyRelease>", self.__check_input)
        # Input polje za unos datuma od
        self.datum_od = DateEntry(self.stanje_kartica_konta, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font="8")
        self.datum_od.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        # Input polje za unos datuma do
        self.datum_do = DateEntry(self.stanje_kartica_konta, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font="8")
        self.datum_do.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Dugme za pokretanje trazenja
        self.pretrazi = Button(self.stanje_kartica_konta, text="Prikaži", command=self.prikazi)
        self.pretrazi.grid(row=1, column=5, padx=10, pady=10, sticky='ew')

        ##########################################################################################
        # Drugi frame - tabela
        self.drugi_frame = Frame(self.prozor_kartica_konta)
        self.drugi_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.drugi_frame.columnconfigure(0, weight=1)
        self.drugi_frame.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_tabela_kartica = Canvas(self.drugi_frame)
        self.canvas_tabela_kartica.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_kartica.columnconfigure(0, weight=1)
        self.canvas_tabela_kartica.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25, fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])
        self.tree_tabela_kartica = ttk.Treeview(self.canvas_tabela_kartica)
        self.tree_tabela_kartica.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.tree_tabela_kartica['columns'] = ("Broj naloga", "Datum", "Duguje", "Potrazuje")
        self.tree_tabela_kartica.column("#0", width=0, stretch=False)
        self.tree_tabela_kartica.column("Broj naloga", anchor=tk.CENTER, minwidth=100)
        self.tree_tabela_kartica.column("Datum", anchor=tk.CENTER, width=100)
        self.tree_tabela_kartica.column("Duguje", anchor=tk.E, width=100)
        self.tree_tabela_kartica.column("Potrazuje", anchor=tk.E, width=100)

        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_kartica)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_kartica.yview)
        self.tree_tabela_kartica.configure(yscrollcommand=self.treeScroll.set)

        self.tree_tabela_kartica.heading("#0", anchor=tk.W, text="")
        self.tree_tabela_kartica.heading("Broj naloga", anchor=tk.CENTER, text="Broj naloga")
        self.tree_tabela_kartica.heading("Datum", anchor=tk.CENTER, text="Datum")
        self.tree_tabela_kartica.heading("Duguje", anchor=tk.CENTER, text="Duguje")
        self.tree_tabela_kartica.heading("Potrazuje", anchor=tk.CENTER, text="Potrazuje")

        # Treci frame za duguje potrazuje saldo
        self.treci_frame = LabelFrame(self.prozor_kartica_konta, text="Saldo analitičke kartice konta")
        self.treci_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.treci_frame.columnconfigure(0, weight=1)
        self.treci_frame.columnconfigure(1, weight=1)
        self.treci_frame.columnconfigure(2, weight=1)
        self.treci_frame.columnconfigure(3, weight=1)
        self.treci_frame.columnconfigure(4, weight=1)
        self.treci_frame.columnconfigure(5, weight=1)
        self.treci_frame.rowconfigure(0, weight=1)

        self.saldo_duguje_text = Label(self.treci_frame, text="Duguje:")
        self.saldo_duguje_text.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.saldo_unos_duguje = Label(self.treci_frame, bg="white", font="10", justify="right", text='',
                                       borderwidth=2, relief="groove", width=20)
        self.saldo_unos_duguje.grid(row=0, column=1, padx=10, pady=10, ipadx=5, ipady=5, sticky='w')

        self.saldo_potrazuje_text = Label(self.treci_frame, text="Potrazuje:")
        self.saldo_potrazuje_text.grid(row=0, column=2, padx=10, pady=10, sticky='e')

        self.saldo_unos_potrazuje = Label(self.treci_frame, bg="white", font="10", justify="right", text='',
                                          borderwidth=2, relief="groove", width=20)
        self.saldo_unos_potrazuje.grid(row=0, column=3, padx=10, pady=10, ipadx=5, ipady=5, sticky='w')

        self.saldo_ukupno_text = Label(self.treci_frame, text="Saldo:")
        self.saldo_ukupno_text.grid(row=0, column=4, padx=10, pady=10, sticky='e')

        self.saldo_ukupno = Label(self.treci_frame, bg="white", font="10", justify="right", text='', borderwidth=2, relief="groove", width=20)
        self.saldo_ukupno.grid(row=0, column=5, padx=10, pady=10, ipadx=5, ipady=5, sticky='w')

        # Cetvrti frame - dugme za detalje
        self.cetvrti_frame = Frame(self.prozor_kartica_konta)
        self.cetvrti_frame.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')
        self.cetvrti_frame.columnconfigure(0, weight=1)
        self.cetvrti_frame.columnconfigure(1, weight=1)
        self.cetvrti_frame.columnconfigure(2, weight=1)
        self.cetvrti_frame.columnconfigure(3, weight=1)
        self.cetvrti_frame.columnconfigure(4, weight=1)
        self.cetvrti_frame.columnconfigure(5, weight=1)
        self.cetvrti_frame.rowconfigure(0, weight=1)

        self.dugme_detalji = Button(self.cetvrti_frame, text="Detalji", bg="#265073", fg="white", command=self.pregledaj_nalog)
        self.dugme_detalji.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.stampa_kartice = Button(self.cetvrti_frame, text="Štampa kartice", bg="#265073", fg="white", command=self.stampaj_karticu)
        self.stampa_kartice.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
