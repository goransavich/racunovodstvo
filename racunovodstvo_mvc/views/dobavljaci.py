from tkinter import ttk, Label, Frame, Button, LabelFrame, Entry, Canvas, Toplevel,messagebox
from racunovodstvo_mvc.controllers.DobavljacController import DobavljacController
from racunovodstvo_mvc.controllers.KeyboardController import KeyboardController
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
import tkinter as tk

class Dobavljaci:
    # Provera koja tastatura se koristi za unos, ako je cirilica vratiti upozorenje, jer mogu samo da se unose latinicna slova- zbog stampe PDF
    def __proveri_jezik_dobavljac(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "Možete koristiti samo latinična slova!!", parent=self.prozor_unos_dobavljaca)
            self.naziv_dobavljaca_entry.delete(0, 'end')

    # Ucitava iz baze sve dobavljace
    def ucitaj_sve_dobavljace(self):
        try:
            conn = DobavljacController()
            return conn.read()
        except ValueError:
            messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom povezivanja na bazu podataka!!",
                                   parent=self.prozor_unos_dobavljaca)

    # Selektovanje izabranog reda u tabeli - Dobavljaci
    def izaberi_red_dobavljaca(self, e):
        # Prvo isprazniti polja
        self.pib_dobavljaca_entry.delete(0, 'end')
        self.naziv_dobavljaca_entry.delete(0, 'end')
        # Uzeti identifikator reda
        selected = self.my_tree_dobavljaci.focus()
        # Uzamanje vrednosti iz izabranog reda
        # Mora ovaj try exept jer selektuje i header tabele, a onda vraća grešku out of range
        try:
            values = self.my_tree_dobavljaci.item(selected, 'values')
            # Prikaz vrednosti u entry poljima
            self.pib_dobavljaca_entry.insert(0, values[2])
            self.naziv_dobavljaca_entry.insert(0, values[1])
        except IndexError:
            pass

    # Prikazuje u tabeli sve dobavljace
    def prikaz_svih_dobavljaca(self):
        # povezivanje na bazu i preuzimanje konta iz tabele
        rezultat = self.ucitaj_sve_dobavljace()
        # global count_konto
        count_dobavljac = 0

        for record in rezultat:
            redni_broj = count_dobavljac + 1
            if count_dobavljac % 2 == 0:
                self.my_tree_dobavljaci.insert(parent='', index='end', iid=record[0], text='',
                                               values=(redni_broj, record[1], record[2]),
                                               tags=('evenrow',))
            else:
                self.my_tree_dobavljaci.insert(parent='', index='end', iid=record[0], text='',
                                               values=(redni_broj, record[1], record[2]),
                                               tags=('oddrow',))
            count_dobavljac += 1

    def dobavljac_postoji(self, pib):
        conn = DobavljacController()
        return conn.pronadji_dobavljaca(pib)

    def pronadji_poslednji_slog_konto(self):
        conn = KontoController()
        return conn.pronadji_poslednji_konto()[0][0]

    def unesi_dobavljaca_u_bazu(self, pib, naziv, id_konta):
        conn = DobavljacController()
        conn.unos_dobavljaca_u_tabelu(pib, naziv, id_konta)

    # Očisti polja za unos Dobavljaca
    def ocisti_polja_dobavljaca(self):
        self.pib_dobavljaca_entry.delete(0, 'end')
        self.naziv_dobavljaca_entry.delete(0, 'end')

    # Unos dobavljaca
    def unos_dobavljaca(self):
        pib_dobavljaca = str(self.pib_dobavljaca_entry.get())
        naziv_dobavljaca = self.naziv_dobavljaca_entry.get()
        # Provera da li je polje za unos prazno
        if naziv_dobavljaca == '' or pib_dobavljaca == '':
            messagebox.showwarning("Greška", "Morate popuniti sva polja!", parent=self.prozor_unos_dobavljaca)
        else:
            # prvo se proverava da li PIB ima devet karaktera
            if len(pib_dobavljaca) == 9:
                # zatim se proverava da li postoji dobavljac sa unetim PIB-om
                postoji_dobavljac = self.dobavljac_postoji(pib_dobavljaca)[0][0]
                if postoji_dobavljac > 0:
                    messagebox.showwarning("Hmmmm", "Dobavljač sa ovim PIB-om već postoji u bazi!", parent=self.prozor_unos_dobavljaca)
                else:
                    # kreiranje novog konta 252111 sa unetim dobavljacem
                    novi_konto = "252111-" + naziv_dobavljaca
                    novi_naziv = 'Dobavljači u zemlji ' + naziv_dobavljaca
                    vrsta = 'subanalitika'
                    try:
                        conn = KontoController()
                        conn.insert_konto(novi_konto, novi_naziv, vrsta)
                    except ValueError:
                        messagebox.showinfo("Greška", "Hmmmmm prilikom unosa dobavljača, pokušajte ponovo!", parent=self.prozor_unos_dobavljaca)
                    # Brisanje entry polja nakon unosa dobavljaca
                    self.pib_dobavljaca_entry.delete(0, 'end')
                    self.naziv_dobavljaca_entry.delete(0, 'end')
                    self.pib_dobavljaca_entry.focus()
                    # Brisanje tabele zbog azuriranja novog konta i dobavljaca
                    self.my_tree_dobavljaci.delete(*self.my_tree_dobavljaci.get_children())
                    #self.my_tree_konto.delete(*self.my_tree_konto.get_children())
                    # pronadji poslednji red u tabeli konto da se dobije ID ovog konta
                    id_konta_dobavljaca = self.pronadji_poslednji_slog_konto()
                    # unesi dobavljaca u tabelu dobavljaci
                    try:
                        self.unesi_dobavljaca_u_bazu(pib_dobavljaca, naziv_dobavljaca, id_konta_dobavljaca)
                        self.prikaz_svih_dobavljaca()
                    except ValueError:
                        messagebox.showinfo("Greška", "Hmmmmm prilikom unosa dobavljača, pokušajte ponovo!", parent=self.prozor_unos_dobavljaca)
            else:
                messagebox.showinfo("Greška", "PIB mora da sadrži 9 cifara!", parent=self.prozor_unos_dobavljaca)

    # pronadji id konta od izabranog dobavljaca koji se azurira
    def pronadji_id_konta_dobavljaca(self, pib):
        conn_dobavljac = DobavljacController()
        rezultat = conn_dobavljac.pronadji_dobavljaca_svi_podaci(pib)
        return rezultat[0][3]

    # kada se azurira naziv dobavljaca u tabeli dobavljaci, istovremeno se azurira i konto dobavljaca u tabeli konto
    def azuriraj_naziv_u_tabeli_konta(self, idkonta, naziv_dobavljaca):
        conn_konto = KontoController()
        oznaka_konta = "252111-{}".format(naziv_dobavljaca)
        conn_konto.update_konto(oznaka_konta, naziv_dobavljaca, idkonta)

    def izmeni_dobavljaca(self):
        # Uzeti identifikator reda
        selected = self.my_tree_dobavljaci.focus()
        if selected:
            values1 = self.my_tree_dobavljaci.item(selected, 'values')
            # Prikaz vrednosti u entry poljima
            izabran_pib = values1[2]
            id_tabele_konta = str(self.pronadji_id_konta_dobavljaca(izabran_pib))
            promenjen_pib = self.pib_dobavljaca_entry.get()
            promenjen_naziv_dobavljaca = self.naziv_dobavljaca_entry.get()

            # Ovde se prvo proverava da li je se menja PIB - ne sme se menjati pib
            if izabran_pib == promenjen_pib:
                self.my_tree_dobavljaci.item(selected, values=(promenjen_pib, promenjen_naziv_dobavljaca), )
                try:
                    # povezivanje na bazu i azuriranje dobavljaca iz tabele
                    conn = DobavljacController()
                    conn.update_dobavljaca(promenjen_naziv_dobavljaca, selected)
                    # povezivanje na bazu i azuriranje dobavljaca u tabeli konta, npr 252111-telek.
                    self.azuriraj_naziv_u_tabeli_konta(id_tabele_konta, promenjen_naziv_dobavljaca)
                    # Brisanje entry polja nakon azuriranja dobavljaca
                    self.ocisti_polja_dobavljaca()
                    self.pib_dobavljaca_entry.focus()
                    # Brisanje tabele zbog azuriranja novog konta
                    self.my_tree_dobavljaci.delete(*self.my_tree_dobavljaci.get_children())
                    # povezivanje na bazu i prikaz u tabeli
                    self.prikaz_svih_dobavljaca()
                except ValueError:
                    messagebox.showinfo("Greška", "Hmmmmm nešto nije u redu sa bazom podataka, pokušajte ponovo!",
                                        parent=self.prozor_unos_dobavljaca)
            else:
                messagebox.showwarning("Greška", "Ne možeš menjati PIB dobavljača već samo naziv! Ako moraš da menjaš PIB, onda obriši dobavljača, pa unesi novog sa ispravnim PIB-om.",
                                       parent=self.prozor_unos_dobavljaca)

        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jednog dobavljača!", parent=self.prozor_unos_dobavljaca)

    def pronadji_konta_u_stavkama_naloga(self, konto_id):
        konekcija_stavke_naloga = StavkaNalogaController()
        return len(konekcija_stavke_naloga.koliko_konta_u_stavkama(konto_id))

    def obrisi_dobavljaca(self):
        # Uzeti identifikator reda
        selected = self.my_tree_dobavljaci.focus()
        if selected:
            values1 = self.my_tree_dobavljaci.item(selected, 'values')
            izabran_pib = values1[2]

            id_tabele_konta = str(self.pronadji_id_konta_dobavljaca(izabran_pib))

            pronadjen_dobavljac_tabela_konto = self.pronadji_konta_u_stavkama_naloga(id_tabele_konta)
            if pronadjen_dobavljac_tabela_konto > 0:
                messagebox.showwarning("Greska", "Ne možete obrisati ovog dobavljaca jer postoji knjiženje sa njim!!",
                                       parent=self.prozor_unos_dobavljaca)
            else:
                # obrisati dobavljaca u tabeli dobavljaci
                conn = DobavljacController()
                conn.delete_dobavljaca(selected)
                # Brisanje entry polja nakon brisanja konta
                self.ocisti_polja_dobavljaca()
                # Brisanje tabele zbog azuriranja novog konta
                self.my_tree_dobavljaci.delete(*self.my_tree_dobavljaci.get_children())
                # povezivanje na bazu i prikaz u tabeli
                self.prikaz_svih_dobavljaca()
                # obrisati 252111-dobavljac u tabeli konta
                conn = KontoController()
                conn.delete_konto(id_tabele_konta)

                # Pop up sa porukom o obrisanom kontu
                messagebox.showinfo("Obrisano", "Dobavljač je uspešno obrisan!", parent=self.prozor_unos_dobavljaca)
        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jednog dobavljača!",
                                   parent=self.prozor_unos_dobavljaca)

    def __init__(self):
        self.prozor_unos_dobavljaca = Toplevel()
        self.prozor_unos_dobavljaca.attributes('-topmost', 'true')
        self.prozor_unos_dobavljaca.grab_set()
        self.prozor_unos_dobavljaca.title("Pregled i unos dobavljaca")
        self.prozor_unos_dobavljaca.geometry("800x600")
        self.prozor_unos_dobavljaca.resizable(0, 0)
        self.prozor_unos_dobavljaca.columnconfigure(0, weight=1)
        self.prozor_unos_dobavljaca.rowconfigure(0, weight=4)
        self.prozor_unos_dobavljaca.rowconfigure(1, weight=1)
        self.prozor_unos_dobavljaca.rowconfigure(2, weight=1)

        # Prvi label frame - tabela sa spiskom dobavljaca
        self.list_svi_dobavljaci = Frame(self.prozor_unos_dobavljaca)
        self.list_svi_dobavljaci.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.list_svi_dobavljaci.columnconfigure(0, weight=1)
        self.list_svi_dobavljaci.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_pregled_dobavljaca = Canvas(self.list_svi_dobavljaci)
        self.canvas_pregled_dobavljaca.grid(row=0, column=0, sticky='nsew')
        self.canvas_pregled_dobavljaca.columnconfigure(0, weight=1)
        self.canvas_pregled_dobavljaca.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style_dobavljaci = ttk.Style()
        self.style_dobavljaci.theme_use('default')
        self.style_dobavljaci.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                                        fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style_dobavljaci.map('Treeview', background=[('selected', '#347083')])

        # Kreiranje canvasa za tabelu jer ne moze scroll bar da ide na Frame ili LabelFrame
        self.my_tree_dobavljaci = ttk.Treeview(self.canvas_pregled_dobavljaca)
        self.my_tree_dobavljaci.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.my_tree_dobavljaci['columns'] = ("Rb", "Naziv", "PIB")
        self.my_tree_dobavljaci.column("#0", width=0, stretch=False)
        self.my_tree_dobavljaci.column("Rb", anchor=tk.W, minwidth=10)
        self.my_tree_dobavljaci.column("Naziv", anchor=tk.W, minwidth=500)
        self.my_tree_dobavljaci.column("PIB", anchor=tk.W, minwidth=160)

        # Kreiranje vertikalnog scroll bara za tabelu
        self.treeDobavljaciScroll = ttk.Scrollbar(self.canvas_pregled_dobavljaca)
        self.treeDobavljaciScroll.grid(row=0, column=1, sticky='ns')
        self.treeDobavljaciScroll.configure(command=self.my_tree_dobavljaci.yview)
        self.my_tree_dobavljaci.configure(yscrollcommand=self.treeDobavljaciScroll.set)

        self.my_tree_dobavljaci.heading("#0", anchor=tk.W, text="")
        self.my_tree_dobavljaci.heading("Rb", anchor=tk.W, text="Rb")
        self.my_tree_dobavljaci.heading("Naziv", anchor=tk.W, text="Naziv")
        self.my_tree_dobavljaci.heading("PIB", anchor=tk.W, text="PIB")

        # Odredjivanje boje u redovima tabele - bela i plava, parni i neparni red
        self.my_tree_dobavljaci.tag_configure('oddrow', background="white")
        self.my_tree_dobavljaci.tag_configure('evenrow', background="lightblue")

        # *********** ovde ide prikaz tabele *******#
        self.prikaz_svih_dobavljaca()
        # Drugi label frame - dva textboxa za unos piba i naziva dobavljaca
        self.entry_dobavljac = LabelFrame(self.prozor_unos_dobavljaca, text="Unos dobavljača")
        self.entry_dobavljac.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.entry_dobavljac.columnconfigure(0, weight=1)
        self.entry_dobavljac.columnconfigure(1, weight=1)
        self.entry_dobavljac.columnconfigure(2, weight=1)
        self.entry_dobavljac.columnconfigure(3, weight=1)
        self.entry_dobavljac.rowconfigure(0, weight=1)

        self.pib_dobavljaca_label = Label(self.entry_dobavljac, text="PIB:")
        self.pib_dobavljaca_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.pib_dobavljaca_entry = Entry(self.entry_dobavljac)
        self.pib_dobavljaca_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.naziv_dobavljaca_label = Label(self.entry_dobavljac, text="Naziv dobavljača:")
        self.naziv_dobavljaca_label.grid(row=0, column=2, padx=10, pady=10, sticky='e')

        self.naziv_dobavljaca_entry = Entry(self.entry_dobavljac)
        self.naziv_dobavljaca_entry.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
        self.naziv_dobavljaca_entry.bind("<KeyRelease>", self.__proveri_jezik_dobavljac)

        # Treci label frame - dugmad za unos, brisanje ...
        self.polje_dugmad_dobavljac = LabelFrame(self.prozor_unos_dobavljaca, text="Komande", bg="lightblue")
        self.polje_dugmad_dobavljac.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')
        self.polje_dugmad_dobavljac.rowconfigure(0, weight=1)
        self.polje_dugmad_dobavljac.columnconfigure(0, weight=1)
        self.polje_dugmad_dobavljac.columnconfigure(1, weight=1)
        self.polje_dugmad_dobavljac.columnconfigure(2, weight=1)
        self.polje_dugmad_dobavljac.columnconfigure(3, weight=1)
        self.polje_dugmad_dobavljac.columnconfigure(4, weight=1)
        self.polje_dugmad_dobavljac.columnconfigure(5, weight=1)

        self.dugme_dodaj_dobavljaca = Button(self.polje_dugmad_dobavljac, text="Dodaj dobavljača", bg='#40A2D8',
                                             fg='white',
                                             command=self.unos_dobavljaca)
        self.dugme_dodaj_dobavljaca.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.dugme_izmeni_dobavljaca = Button(self.polje_dugmad_dobavljac, text="Izmeni dobavljača", bg="#265073",
                                              fg="white",
                                              command=self.izmeni_dobavljaca)
        self.dugme_izmeni_dobavljaca.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.dugme_obrisi_dobavljaca = Button(self.polje_dugmad_dobavljac, text="Obriši dobavljača", bg="#FF6868",
                                              fg="white",
                                              command=self.obrisi_dobavljaca)
        self.dugme_obrisi_dobavljaca.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        self.dugme_izaberi_dobavljaca = Button(self.polje_dugmad_dobavljac, text="Očisti polja za unos",
                                               command=self.ocisti_polja_dobavljaca)
        self.dugme_izaberi_dobavljaca.grid(row=0, column=4, padx=10, pady=10, sticky='ew')

        # Selektovanje reda iz tabele klikom na slog
        self.my_tree_dobavljaci.bind("<ButtonRelease-1>", self.izaberi_red_dobavljaca)