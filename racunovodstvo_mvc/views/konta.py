from tkinter import ttk, Button, Toplevel, LabelFrame, Frame, Canvas, Label, Entry, messagebox
from racunovodstvo_mvc.controllers.KeyboardController import KeyboardController
import tkinter as tk
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.controllers.DobavljacController import DobavljacController


class Konta:

    def __proveri_jezik_konto_oznaka(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "Prebacite na latiničnu tastaturu, možete koristiti samo latinična slova!!", parent=self.prozor_unesi_konto)
            self.konto_entry.delete(0, 'end')

    def __proveri_jezik_konto_naziv(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "Možete koristiti samo latinična slova!!", parent=self.prozor_unesi_konto)
            self.naziv_entry.delete(0, 'end')

    # Ucitava iz baze sva konta za prikaz u tabeli
    def ucitaj_sva_konta(self):
        try:
            conn = KontoController()
            return conn.read()
        except ValueError:
            messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom povezivanja na bazu podataka!!", parent=self.prozor_unesi_konto)

    # Prikaz svih konta u tabeli
    def prikaz_sva_konta(self):
        # povezivanje na bazu i preuzimanje konta iz tabele

        rezultat = self.ucitaj_sva_konta()

        #global count_konto
        count_konto = 0

        for record in rezultat:
            if count_konto % 2 == 0:
                self.my_tree_konto.insert(parent='', index='end', iid=record[0], text='',
                                     values=(record[1], record[2]),
                                     tags=('evenrow',))
            else:
                self.my_tree_konto.insert(parent='', index='end', iid=record[0], text='',
                                     values=(record[1], record[2]),
                                     tags=('oddrow',))
            count_konto += 1

    # Očisti polja za unos konta i naziva
    def ocisti_polja(self):
        self.konto_entry.delete(0, 'end')
        self.naziv_entry.delete(0, 'end')

    # Odredjivanje koliko karaktera ima u oznaci konta - treba da ima bar 6
    def __broj_karaktera(self, konto):
        if len(konto) < 6:
            return True
        else:
            return False

    # Selektovanje izabranog reda u tabeli - Konta
    def izaberi_red(self, e):
        # Prvo isprazniti polja
        self.konto_entry.delete(0, 'end')
        self.naziv_entry.delete(0, 'end')
        # Uzeti identifikator reda
        selected = self.my_tree_konto.focus()
        # Uzamanje vrednosti iz izabranog reda
        # Mora ovaj try exept jer selektuje i header tabele, a onda vraća grešku out of range
        try:
            values = self.my_tree_konto.item(selected, 'values')
            # Prikaz vrednosti u entry poljima
            self.konto_entry.insert(0, values[0])
            self.naziv_entry.insert(0, values[1])
        except IndexError:
            pass

    def __pronadji_konto_po_id(self, konto_id):
        conn_konto = KontoController()
        return conn_konto.find_id(konto_id)

    def __odredi_vrstu_konta_brisanje(self, konto_id):
        pronadjen_konto = self.__pronadji_konto_po_id(konto_id)
        return pronadjen_konto[0][3]

    def __pronadji_subanaliticka_konta_u_tabeli_konto(self, konto_id, duzina):
        pronadjen_konto = self.__pronadji_konto_po_id(konto_id)
        oznaka = pronadjen_konto[0][1]
        skracena_oznaka = oznaka[0:duzina]
        # Prvo pronaci sva subanaliticka konta koja imaju ovakve oznake, odnosno njihove ID, a onda u stavkama pronaci da li postoji neki od ovih konta
        konekcija_stavke_naloga = KontoController()
        rezultat = konekcija_stavke_naloga.deo_konta_postoji(skracena_oznaka)
        if len(rezultat) > 1:
            return True
        else:
            return False

    def __brisanje_slobodnog_konta(self, konto_id):
        conn = KontoController()
        conn.delete_konto(konto_id)
        # Brisanje entry polja nakon brisanja konta
        self.ocisti_polja()
        # Brisanje tabele zbog azuriranja novog konta
        self.my_tree_konto.delete(*self.my_tree_konto.get_children())
        # povezivanje na bazu i prikaz u tabeli
        self.prikaz_sva_konta()
        # Pop up sa porukom o obrisanom kontu
        messagebox.showinfo("Obrisano", "Konto je uspešno obrisan!", parent=self.prozor_unesi_konto)

    def __pronadji_konta_u_stavkama_naloga(self, konto_id):
        konekcija_stavke_naloga = StavkaNalogaController()
        return len(konekcija_stavke_naloga.koliko_konta_u_stavkama(konto_id))

    def __konto_subanalitika_postoji_stavka_naloga(self, konto_id):
        if self.__pronadji_konta_u_stavkama_naloga(konto_id) > 0:
            messagebox.showwarning("Greska", "Ne možete obrisati ovaj konto jer postoji knjiženje sa njim!!", parent=self.prozor_unesi_konto)
        else:
            self.__brisanje_slobodnog_konta(konto_id)

    def __konto_analitika_postoji_subanalitika(self, konto_id):
        if self.__pronadji_subanaliticka_konta_u_tabeli_konto(konto_id, 5):
            messagebox.showwarning("Greska", "Ne možete obrisati ovaj konto jer sadrži podredjena subanalitička konta!!", parent=self.prozor_unesi_konto)
        else:
            self.__brisanje_slobodnog_konta(konto_id)

    def __konto_sintetika_postoji_subanalitika(self, konto_id):
        if self.__pronadji_subanaliticka_konta_u_tabeli_konto(konto_id, 4):
            messagebox.showwarning("Greska", "Ne možete obrisati ovaj konto jer sadrži podredjena analitička konta!!", parent=self.prozor_unesi_konto)
        else:
            self.__brisanje_slobodnog_konta(konto_id)

    def __konto_grupa_postoji_subanalitika(self, konto_id):
        if self.__pronadji_subanaliticka_konta_u_tabeli_konto(konto_id, 3):
           messagebox.showwarning("Greska", "Ne možete obrisati ovaj konto jer sadrži podredjena sintetička konta!", parent=self.prozor_unesi_konto)
        else:
            self.__brisanje_slobodnog_konta(konto_id)

    def __konto_kategorija_postoji_subanalitika(self, konto_id):
        if self.__pronadji_subanaliticka_konta_u_tabeli_konto(konto_id, 2):
            messagebox.showwarning("Greska", "Ne možete obrisati ovaj konto jer sadrži podredjena konta!!", parent=self.prozor_unesi_konto)
        else:
            self.__brisanje_slobodnog_konta(konto_id)

    def __konto_klasa_postoji_subanalitika(self, konto_id):
        if self.__pronadji_subanaliticka_konta_u_tabeli_konto(konto_id, 1):
            messagebox.showwarning("Greska", "Ne možete obrisati ovaj konto jer sadrži podredjena konta!!", parent=self.prozor_unesi_konto)
        else:
            self.__brisanje_slobodnog_konta(konto_id)

    # Brisanje konta
    def obrisi_konto(self):
        # Brisanje iz tabele treeview
        selected = self.my_tree_konto.focus()

        if selected:
            values1 = self.my_tree_konto.item(selected, 'values')
            naziv_konta = values1[0]
            if naziv_konta.startswith("252111-"):
                messagebox.showwarning("Sugestija", "Ako želiš da obrišeš dobavljača, uradi to u tabeli Dobavljači!!",
                                       parent=self.prozor_unesi_konto)
            else:
                # Provera da li konto ima saldo, odnosno da li je koriscen u stavkama naloga###
                # Prvo utvrditi koja je vrsta konta: klasa, grupa, analitika, dobavljac... funkcija vraca string sa nazivom vrste konta
                vrsta_konta = self.__odredi_vrstu_konta_brisanje(selected)
                # Brisanje iz baze podataka
                try:
                    # if elif - na osnovu vrste konta utvrditi brisanje, ako je subanalitika, proveri se saldo i ako nema-brise se, ako ima - pojavljuje se poruka
                    if vrsta_konta == 'subanalitika':
                        self.__konto_subanalitika_postoji_stavka_naloga(selected)
                    elif vrsta_konta == 'analitika':
                        self.__konto_analitika_postoji_subanalitika(selected)
                    elif vrsta_konta == 'sintetika':
                        self.__konto_sintetika_postoji_subanalitika(selected)
                    elif vrsta_konta == 'grupa':
                        self.__konto_grupa_postoji_subanalitika(selected)
                    elif vrsta_konta == 'kategorija':
                        self.__konto_kategorija_postoji_subanalitika(selected)
                    elif vrsta_konta == 'klasa':
                        self.__konto_klasa_postoji_subanalitika(selected)

                except ValueError:
                    messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom povezivanja na bazu podataka!!", parent=self.prozor_unesi_konto)

        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jedan konto!", parent=self.prozor_unesi_konto)

    # Izmena konta
    def izmeni_konto(self):
        # Uzeti identifikator reda
        selected = self.my_tree_konto.focus()
        if selected:
            values1 = self.my_tree_konto.item(selected, 'values')
            # Prikaz vrednosti u entry poljima
            izabrani_konto = values1[0]
            promenjen_konto = self.konto_entry.get()
            promenjen_naziv = self.naziv_entry.get()[:100]

            # Ovde se prvo proverava da li je izmenjeni konto isti sa nekim koji vec postoji u tabeli (proverava se samo oznaka konta npr.421211)
            if izabrani_konto == promenjen_konto:
                # ovde ne treba dozvoliti izmenu konta dobavljaca, vec korisnika uputiti na prozor Dobavljaci
                if izabrani_konto.startswith("252111-"):
                    messagebox.showwarning("Sugestija", "Ako želiš da menjaš naziv dobavljača, uradi to u prozoru Dobavljači!", parent=self.prozor_unesi_konto)
                    self.naziv_entry.delete(0, 'end')
                    self.naziv_entry.insert(0, values1[1])
                else:
                    try:
                        # povezivanje na bazu i preuzimanje konta iz tabele
                        conn = KontoController()
                        conn.update_konto(promenjen_konto, promenjen_naziv, selected)
                        self.my_tree_konto.item(selected, values=(promenjen_konto, promenjen_naziv), )
                        # Brisanje entry polja nakon azuriranja konta
                        self.ocisti_polja()
                        self.konto_entry.focus()
                        # Brisanje tabele zbog azuriranja novog konta
                        self.my_tree_konto.delete(*self.my_tree_konto.get_children())
                        # povezivanje na bazu i prikaz u tabeli
                        self.prikaz_sva_konta()
                    except ValueError:
                        messagebox.showinfo("Greška", "Hmmmmm nešto nije u redu sa bazom podataka, pokušajte ponovo!",
                                            parent=self.prozor_unesi_konto)
            else:
                messagebox.showwarning("Greška", "Ne možete menjati oznaku konta već samo naziv!", parent=self.prozor_unesi_konto)
        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jedan konto!", parent=self.prozor_unesi_konto)

    # Provera da li već postoji unet konto
    def __provera_unet_konto(self, oznaka_konta):
        conn = KontoController()
        return conn.check_konto_exist(oznaka_konta)

    # Provera da li je unet nadredjeni konto
    def __provera_nadredjen_konto(self, oznaka_konta):
        # Prvo skinuti prvu cifru
        skracen = oznaka_konta[1:6]
        # Naci poziciju nule u kontu da se odredi vrsta konta
        pozicija = skracen.find("0")
        # Dodaje se nula da se odredi nadredjeni konto
        skraceni_konto = oznaka_konta[:pozicija]
        # Konto se popunjava sa nulama na kraju do sestog mesta
        nadredjeni_konto = skraceni_konto.ljust(6, '0')

        conn = KontoController()
        return conn.check_konto_exist(nadredjeni_konto)

    def __odredi_vrstu_konta(self, konto):
        skracen_konto_prva_cifra = konto[1:6]
        broj_nula = skracen_konto_prva_cifra.count("0")

        if broj_nula == 0:
            return "subanalitika"
        if broj_nula == 1:
            return "analitika"
        if broj_nula == 2:
            return "sintetika"
        if broj_nula == 3:
            return "grupa"
        if broj_nula == 4:
            return "kategorija"
        if broj_nula == 5:
            return "klasa"

    # Unos novog konta
    def unos_konta(self):
        novi_konto = self.konto_entry.get()[:50]
        novi_naziv = self.naziv_entry.get()[:100]
        nova_vrsta = self.__odredi_vrstu_konta(novi_konto)
        # Proverava se da li konto ima 00000, u tom slucaju je u pitanju klasa pa ne treba traziti unos nadredjene klase
        za_proveru = novi_konto[1:6]
        # Ova provera ide jer mogu da se unose subsubanaliticka konta, pa bi onda prijavljivao gresku, jer se pored 6 cifara unose i slova
        provera_zbog_subanalitike = novi_konto[0:6]
        # Provera da li su polja za unos prazna
        if novi_konto == '' or novi_naziv == '':
            messagebox.showwarning("Greška", "Morate popuniti oba polja!", parent=self.prozor_unesi_konto)
        # Provera da li oznaka konta ima minimum 6 karaktera
        elif self.__broj_karaktera(novi_konto):
            messagebox.showwarning("Greška", "Oznaka konta nije dobra!!", parent=self.prozor_unesi_konto)
        # Provera da li vec postoji unet konto
        elif not self.__provera_unet_konto(novi_konto):
            # Pre unosa novog konta, proveriti da li je unet nadredjeni konto
            if (self.__provera_nadredjen_konto(provera_zbog_subanalitike)) or (za_proveru == "00000"):
                conn = KontoController()
                conn.insert_konto(novi_konto, novi_naziv, nova_vrsta)
                # Brisanje entry polja nakon azuriranja konta
                self.ocisti_polja()
                self.konto_entry.focus()
                # Brisanje tabele zbog azuriranja novog konta
                self.my_tree_konto.delete(*self.my_tree_konto.get_children())

                # povezivanje na bazu i prikaz u tabeli
                self.prikaz_sva_konta()
            else:
                messagebox.showwarning("Greška", "Morate uneti nadredjeni konto!", parent=self.prozor_unesi_konto)
        else:
            messagebox.showwarning("Greška", "Već postoji ovaj konto!", parent=self.prozor_unesi_konto)

    def pronadji_poslednji_slog_konto(self):
        conn = KontoController()
        return conn.pronadji_poslednji_konto()[0][0]

    def __init__(self, master):
        self.master = master
        self.prozor_unesi_konto = Toplevel(self.master)
        self.prozor_unesi_konto.attributes('-topmost', 'true')
        self.prozor_unesi_konto.grab_set()
        self.prozor_unesi_konto.title("Pregled i unos ekonomske klasifikacije")
        # window_width = 900
        # window_height = 850
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        if self.master.winfo_screenwidth() < 1400:
            window_width = self.master.winfo_screenwidth() - 200
        else:
            window_width = self.master.winfo_screenwidth() - 600

        if self.master.winfo_screenheight() < 800:
            window_height = self.master.winfo_screenheight() - 100
        else:
            window_height = self.master.winfo_screenheight() - 280
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        if self.master.winfo_screenheight() < 800:
            y_cordinate = 0
        else:
            y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_unesi_konto.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_unesi_konto.resizable(False, False)
        self.prozor_unesi_konto.columnconfigure(0, weight=1)
        self.prozor_unesi_konto.rowconfigure(0, weight=3)
        self.prozor_unesi_konto.rowconfigure(1, weight=1)
        self.prozor_unesi_konto.rowconfigure(2, weight=1)
        #self.prozor_unesi_konto.rowconfigure(3, weight=1)

        # Prvi frame za spisak svih ekonomskih klasifikacija - tabela
        self.list_sva_konta = Frame(self.prozor_unesi_konto)
        self.list_sva_konta.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.list_sva_konta.columnconfigure(0, weight=1)
        self.list_sva_konta.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_pregled_konta = Canvas(self.list_sva_konta)
        self.canvas_pregled_konta.grid(row=0, column=0, sticky='nsew')
        self.canvas_pregled_konta.columnconfigure(0, weight=1)
        self.canvas_pregled_konta.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25, fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])

        # Kreiranje canvasa za tabelu jer ne moze scroll bar da ide na Frame ili LabelFrame
        self.my_tree_konto = ttk.Treeview(self.canvas_pregled_konta)
        self.my_tree_konto.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.my_tree_konto['columns'] = ("Konto", "Naziv")
        self.my_tree_konto.column("#0", width=0, stretch=False)
        self.my_tree_konto.column("Konto", anchor=tk.W, minwidth=160)
        self.my_tree_konto.column("Naziv", anchor=tk.W, minwidth=500)

        # Kreiranje vertikalnog scroll bara za tabelu
        self.treeKontoScroll = ttk.Scrollbar(self.canvas_pregled_konta)
        self.treeKontoScroll.grid(row=0, column=1, sticky='ns')
        self.treeKontoScroll.configure(command=self.my_tree_konto.yview)
        self.my_tree_konto.configure(yscrollcommand=self.treeKontoScroll.set)

        self.my_tree_konto.heading("#0", anchor=tk.W, text="")
        self.my_tree_konto.heading("Konto", anchor=tk.W, text="Konto")
        self.my_tree_konto.heading("Naziv", anchor=tk.W, text="Naziv")

        # Odredjivanje boje u redovima tabele - bela i plava, parni i neparni red
        self.my_tree_konto.tag_configure('oddrow', background="white")
        self.my_tree_konto.tag_configure('evenrow', background="lightblue")

        # *********** ovde ide prikaz tabele *******#
        self.prikaz_sva_konta()

        # Drugi frame za unos dobavljača

        # Treći frame za entry polja naziv i konto
        self.entry_polja = LabelFrame(self.prozor_unesi_konto, text="Unos konta")
        self.entry_polja.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.entry_polja.columnconfigure(0, weight=1)
        self.entry_polja.columnconfigure(1, weight=1)
        self.entry_polja.columnconfigure(2, weight=1)
        self.entry_polja.columnconfigure(3, weight=6)
        self.entry_polja.rowconfigure(0, weight=1)

        # Label i polje za unos konta
        self.konto_label = Label(self.entry_polja, text="Konto:")
        self.konto_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.konto_entry = Entry(self.entry_polja)
        self.konto_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.konto_entry.bind("<KeyRelease>", self.__proveri_jezik_konto_oznaka)

        # Label i polje za unos naziva ekonomske klasifikacije
        self.naziv_label = Label(self.entry_polja, text="Naziv ekonomske klasifikacije:")
        self.naziv_label.grid(row=0, column=2, padx=10, pady=10, sticky='e')

        self.naziv_entry = Entry(self.entry_polja)
        self.naziv_entry.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
        self.naziv_entry.bind("<KeyRelease>", self.__proveri_jezik_konto_naziv)

        # Četvrti frame za dugmad Dodaj, Izmeni, Obrisi i Izaberi
        self.polje_dugmad = LabelFrame(self.prozor_unesi_konto, text="Komande", bg="lightblue")
        self.polje_dugmad.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.polje_dugmad.rowconfigure(0, weight=1)
        self.polje_dugmad.columnconfigure(0, weight=1)
        self.polje_dugmad.columnconfigure(1, weight=1)
        self.polje_dugmad.columnconfigure(2, weight=1)
        self.polje_dugmad.columnconfigure(3, weight=1)
        self.polje_dugmad.columnconfigure(4, weight=1)
        self.polje_dugmad.columnconfigure(5, weight=1)

        self.dugme_dodaj = Button(self.polje_dugmad, text="Dodaj konto", bg='#40A2D8', fg='white', command=self.unos_konta)
        self.dugme_dodaj.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.dugme_izmeni = Button(self.polje_dugmad, text="Izmeni konto", bg="#265073", fg="white", command=self.izmeni_konto)
        self.dugme_izmeni.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.dugme_obrisi = Button(self.polje_dugmad, text="Obriši konto", bg="#FF6868", fg="white", command=self.obrisi_konto)
        self.dugme_obrisi.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        self.dugme_izaberi = Button(self.polje_dugmad, text="Očisti polja za unos", command=self.ocisti_polja)
        self.dugme_izaberi.grid(row=0, column=4, padx=10, pady=10, sticky='ew')

        # Selektovanje reda iz tabele klikom na slog
        self.my_tree_konto.bind("<ButtonRelease-1>", self.izaberi_red)
