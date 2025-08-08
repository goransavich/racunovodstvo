from racunovodstvo_mvc.controllers.IzvoriController import IzvoriController
from racunovodstvo_mvc.controllers.KeyboardController import KeyboardController
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from tkinter import ttk, Button, Toplevel, LabelFrame, Frame, Canvas, Label, Entry, messagebox
import tkinter as tk

class IzvoriFinansiranja():

    # Provera koja tastatura se koristi za unos, ako je cirilica vratiti upozorenje, jer mogu samo da se unose latinicna slova- zbog stampe PDF

    def __proveri_jezik_sifra(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "Prebacite na latiničnu tastaturu!!", parent=self.prozor_izvor_finansiranja)
            self.sifra_entry_izvori_finansiranja.delete(0, 'end')

    def __proveri_jezik_naziv(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "Prebacite na latiničnu tastaturu!!", parent=self.prozor_izvor_finansiranja)
            self.naziv_entry_izvori_finansiranja.delete(0, 'end')


    def prikaz_svih_izvora(self):
        # povezivanje na bazu i preuzimanje izvora finansiranja iz tabele
        conn = IzvoriController()
        rezultat_izvori_finansiranja = conn.read()

        count_izvori = 0
        for record in rezultat_izvori_finansiranja:
            if count_izvori % 2 == 0:
                self.my_tree_izvori_finansiranja.insert(parent='', index='end', iid=record[0], text='',
                                                   values=(record[1], record[2]),
                                                   tags=('evenrow',))
            else:
                self.my_tree_izvori_finansiranja.insert(parent='', index='end', iid=record[0], text='',
                                                   values=(record[1], record[2]),
                                                   tags=('oddrow',))
            count_izvori += 1

    def izaberi_red_izvor(self, e):
        # Prvo isprazniti polja
        self.sifra_entry_izvori_finansiranja.delete(0, 'end')
        self.naziv_entry_izvori_finansiranja.delete(0, 'end')
        # Uzeti identifikator reda
        selected = self.my_tree_izvori_finansiranja.focus()
        # Uzamanje vrednosti iz izabranog reda
        # Mora ovaj try exept jer selektuje i header tabele, a onda vraća grešku out of range
        try:
            values_izvori = self.my_tree_izvori_finansiranja.item(selected, 'values')
            # Prikaz vrednosti u entry poljima
            self.sifra_entry_izvori_finansiranja.insert(0, values_izvori[0])
            self.naziv_entry_izvori_finansiranja.insert(0, values_izvori[1])
        except IndexError:
            pass

    def ocisti_polje(self):
        self.sifra_entry_izvori_finansiranja.delete(0, 'end')
        self.naziv_entry_izvori_finansiranja.delete(0, 'end')

    # Unos novog izvora finansiranja
    def unos_izvora_finansiranja(self):
        novi_izvor_finansiranja_sifra = self.sifra_entry_izvori_finansiranja.get()
        novi_izvor_finansiranja_naziv = self.naziv_entry_izvori_finansiranja.get()
        ucitaj_kontrolu = KeyboardController()
        jezik = ucitaj_kontrolu.check_language()
        if jezik:
            messagebox.showwarning("Greška", "Možete koristiti samo latinična slova!!", parent=self.prozor_izvor_finansiranja)
            self.naziv_entry_izvori_finansiranja.delete(0, 'end')
        # Provera da li su polja za unos prazna
        elif (novi_izvor_finansiranja_sifra == '' or novi_izvor_finansiranja_naziv == ''):
            messagebox.showwarning("Greška", "Morate popuniti oba polja!", parent=self.prozor_izvor_finansiranja)
        else:
            try:
                conn = IzvoriController()
                conn.insert_izvor(novi_izvor_finansiranja_sifra, novi_izvor_finansiranja_naziv)

                # Brisanje entry polja nakon azuriranja vrste naloga
                self.ocisti_polje()
                # Brisanje tabele zbog azuriranja nove vrste naloga
                self.my_tree_izvori_finansiranja.delete(*self.my_tree_izvori_finansiranja.get_children())
                # povezivanje na bazu i prikaz u tabeli
                self.prikaz_svih_izvora()
                self.sifra_entry_izvori_finansiranja.focus()
            except:
                messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom povezivanja na bazu podataka!!",
                                       parent=self.prozor_izvor_finansiranja)


    # Izmena izvora finansiranja
    def izmeni_izvor_finansiranja(self):
        # Uzeti identifikator reda
        selected = self.my_tree_izvori_finansiranja.focus()
        if selected:
            promenjen_sifra_izvora_finansiranja = self.sifra_entry_izvori_finansiranja.get()
            promenjen_naziv_izvora_finansiranja = self.naziv_entry_izvori_finansiranja.get()
            #self.my_tree_izvori_finansiranja.item(selected, values=(promenjen_sifra_izvora_finansiranja, promenjen_naziv_izvora_finansiranja), )
            ucitaj_kontrolu = KeyboardController()
            jezik = ucitaj_kontrolu.check_language()
            if jezik:
                messagebox.showwarning("Greška", "Možete koristiti samo latinična slova!!", parent=self.prozor_izvor_finansiranja)
                self.naziv_entry_izvori_finansiranja.delete(0, 'end')
            else:
                try:
                    # povezivanje na bazu i preuzimanje vrste naloga iz tabele
                    conn = IzvoriController()
                    conn.update_izvor(promenjen_sifra_izvora_finansiranja, promenjen_naziv_izvora_finansiranja, selected)
                    # Brisanje entry polja nakon azuriranja vrste naloga
                    self.ocisti_polje()
                    # Brisanje tabele zbog azuriranja nove vrste naloga
                    self.my_tree_izvori_finansiranja.delete(*self.my_tree_izvori_finansiranja.get_children())
                    # povezivanje na bazu i prikaz u tabeli
                    self.prikaz_svih_izvora()

                except:
                    messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom izmene izvora finansiranja!!. Pokušajte ponovo.", parent=self.prozor_izvor_finansiranja)
        else:
            messagebox.showwarning("Greska", "Hmmmm, niste izabrali ni jedan izvor finansiranja!", parent=self.prozor_izvor_finansiranja)

    # Brisanje izvora finansiranja
    def obrisi_izvor_finansiranja(self):
        # Brisanje iz tabele treeview
        selected = self.my_tree_izvori_finansiranja.focus()
        if selected:
            x = self.my_tree_izvori_finansiranja.selection()[0]
            ''' Prvo provera da li se ovaj izvor finansiranja nalazi u nekoj stavki naloga - ako da, onda nema brisanja '''
            conn = IzvoriController()
            rezultat = conn.pronadji_oznaku_po_sifri(x)
            sifra_izvora = rezultat[0][0]
            conn_stavke = StavkaNalogaController()
            izvori_u_stavkama = conn_stavke.pronadji_izvore()
            brojac = 0
            for izvor in izvori_u_stavkama:
                if sifra_izvora in izvor: brojac+= 1
            if brojac > 0:
                messagebox.showwarning("Greska", "Ne možete obrisati ovaj izvor finansiranja! On se nalazi u nekoj stavki naloga", parent=self.prozor_izvor_finansiranja)
            else:
                # Brisanje iz baze podataka
                try:
                    conn = IzvoriController()
                    conn.delete_izvor(selected)
                    self.my_tree_izvori_finansiranja.delete(x)
                    # Brisanje entry polja nakon brisanja konta
                    self.ocisti_polje()
                    # Brisanje tabele zbog azuriranja nove vrste naloga
                    self.my_tree_izvori_finansiranja.delete(*self.my_tree_izvori_finansiranja.get_children())
                    # povezivanje na bazu i prikaz u tabeli
                    self.prikaz_svih_izvora()
                    # Pop up sa porukom o obrisanom kontu
                    messagebox.showinfo("Obrisano", "Odabrani izvor finansiranja je obrisan!", parent=self.prozor_izvor_finansiranja)
                except:
                    messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom brisanja izvora finaniranja!! Pokušajte ponovo!", parent=self.prozor_izvor_finansiranja)

        else:
            messagebox.showwarning("Greska", "Hmmmm, niste izabrali ni jedan izvor finansiranja!", parent=self.prozor_izvor_finansiranja)

    def __init__(self):
        self.prozor_izvor_finansiranja = Toplevel()
        self.prozor_izvor_finansiranja.grab_set()
        self.prozor_izvor_finansiranja.title("Pregled i unos izvora finansiranja")
        self.prozor_izvor_finansiranja.geometry("800x600")
        self.prozor_izvor_finansiranja.resizable(0, 0)
        self.prozor_izvor_finansiranja.columnconfigure(0, weight=1)
        self.prozor_izvor_finansiranja.rowconfigure(0, weight=1)
        self.prozor_izvor_finansiranja.rowconfigure(1, weight=3)
        self.prozor_izvor_finansiranja.rowconfigure(2, weight=3)

        # Prvi frame za spisak svih izvora finansiranja - tabela
        self.list_svi_izvori_finansiranja = Frame(self.prozor_izvor_finansiranja)
        self.list_svi_izvori_finansiranja.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.list_svi_izvori_finansiranja.columnconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_izvori_finansiranja = Canvas(self.list_svi_izvori_finansiranja)
        self.canvas_izvori_finansiranja.grid(row=0, column=0, sticky='nsew')
        self.canvas_izvori_finansiranja.columnconfigure(0, weight=1)
        # canvas_vrste_naloga.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                        fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])

        # Kreiranje canvasa za tabelu jer ne moze scroll bar da ide na Frame ili LabelFrame
        self.my_tree_izvori_finansiranja = ttk.Treeview(self.canvas_izvori_finansiranja)
        self.my_tree_izvori_finansiranja.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.my_tree_izvori_finansiranja['columns'] = ("Šifra izvora", "Naziv")
        self.my_tree_izvori_finansiranja.column("#0", width=0, stretch=False)
        self.my_tree_izvori_finansiranja.column("Šifra izvora", anchor=tk.CENTER, width=10)
        self.my_tree_izvori_finansiranja.column("Naziv", anchor=tk.CENTER, minwidth=120)

        # Kreiranje vertikalnog scroll bara za tabelu
        self.treeIzvoriScroll = ttk.Scrollbar(self.canvas_izvori_finansiranja)
        self.treeIzvoriScroll.grid(row=0, column=1, sticky='ns')
        self.treeIzvoriScroll.configure(command=self.my_tree_izvori_finansiranja.yview)
        self.my_tree_izvori_finansiranja.configure(yscrollcommand=self.treeIzvoriScroll.set)

        self.my_tree_izvori_finansiranja.heading("#0", anchor=tk.W, text="")
        self.my_tree_izvori_finansiranja.heading("Šifra izvora", anchor=tk.CENTER, text="Šifra izvora")
        self.my_tree_izvori_finansiranja.heading("Naziv", anchor=tk.CENTER, text="Naziv")

        # Odredjivanje boje u redovima tabele - bela i plava, parni i neparni red
        self.my_tree_izvori_finansiranja.tag_configure('oddrow', background="white")
        self.my_tree_izvori_finansiranja.tag_configure('evenrow', background="lightblue")

        self.prikaz_svih_izvora()

        # Drugi frame za entry polja naziv i konto
        self.entry_polja_izvor = LabelFrame(self.prozor_izvor_finansiranja, text="Unos")
        self.entry_polja_izvor.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.entry_polja_izvor.columnconfigure(0, weight=1)
        self.entry_polja_izvor.columnconfigure(1, weight=1)
        self.entry_polja_izvor.columnconfigure(2, weight=1)
        self.entry_polja_izvor.columnconfigure(3, weight=1)
        self.entry_polja_izvor.rowconfigure(0, weight=1)

        # Label i polje za unos izvora finansiranja
        self.sifra_label_izvori_finansiranja = Label(self.entry_polja_izvor, text="Šifra izvora finansiranja:")
        self.sifra_label_izvori_finansiranja.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.sifra_entry_izvori_finansiranja = Entry(self.entry_polja_izvor)
        self.sifra_entry_izvori_finansiranja.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        self.sifra_entry_izvori_finansiranja.bind("<KeyRelease>", self.__proveri_jezik_sifra)

        self.naziv_label_izvori_finansiranja = Label(self.entry_polja_izvor, text="Naziv izvora finansiranja:")
        self.naziv_label_izvori_finansiranja.grid(row=0, column=2, padx=10, pady=10, sticky='e')

        self.naziv_entry_izvori_finansiranja = Entry(self.entry_polja_izvor)
        self.naziv_entry_izvori_finansiranja.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
        self.naziv_entry_izvori_finansiranja.bind("<KeyRelease>", self.__proveri_jezik_naziv)


        # Treci frame za dugmad Dodaj, Izmeni, Obrisi i Izaberi
        self.polje_dugmad_izvor = LabelFrame(self.prozor_izvor_finansiranja, text="Komande", bg="lightblue")
        self.polje_dugmad_izvor.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.polje_dugmad_izvor.rowconfigure(0, weight=1)
        self.polje_dugmad_izvor.columnconfigure(0, weight=1)
        self.polje_dugmad_izvor.columnconfigure(1, weight=1)
        self.polje_dugmad_izvor.columnconfigure(2, weight=1)
        self.polje_dugmad_izvor.columnconfigure(3, weight=1)

        self.dugme_dodaj_izvor_finansiranja = Button(self.polje_dugmad_izvor, text="Dodaj izvor finansiranja", bg='#40A2D8', fg='white', command=self.unos_izvora_finansiranja)
        self.dugme_dodaj_izvor_finansiranja.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        self.dugme_izmeni_izvor_finansiranja = Button(self.polje_dugmad_izvor, text="Izmeni izvor finansiranja", bg="#265073", fg="white", command=self.izmeni_izvor_finansiranja)
        self.dugme_izmeni_izvor_finansiranja.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.dugme_obrisi_izvor_finansiranja = Button(self.polje_dugmad_izvor, text="Obriši izvor finansiranja", bg="#FF6868", fg="white", command=self.obrisi_izvor_finansiranja)
        self.dugme_obrisi_izvor_finansiranja.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.dugme_izaberi_izvor_finansiranja = Button(self.polje_dugmad_izvor, text="Očisti polja za unos", command=self.ocisti_polje)
        self.dugme_izaberi_izvor_finansiranja.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        # Selektovanje reda iz tabele klikom na slog
        self.my_tree_izvori_finansiranja.bind("<ButtonRelease-1>", self.izaberi_red_izvor)