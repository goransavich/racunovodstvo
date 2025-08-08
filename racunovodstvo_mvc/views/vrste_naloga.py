from tkinter import ttk, Label, Frame, Button, LabelFrame, Entry, Canvas, Toplevel,messagebox
from racunovodstvo_mvc.controllers.VrstenalogaController import VrstenalogaController
from racunovodstvo_mvc.controllers.KeyboardController import KeyboardController
import tkinter as tk

class VrsteNaloga:

    # Provera koja tastatura se koristi za unos, ako je cirilica vratiti upozorenje, jer mogu samo da se unose latinicna slova- zbog stampe PDF
    def __proveri_jezik(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "Možete koristiti samo latinična slova!!", parent=self.prozor_vrste_naloga)
            self.naziv_entry_nalog.delete(0, 'end')

    def sve_vrste_naloga(self):
        # povezivanje na bazu i preuzimanje konta iz tabele
        conn_pretraga = VrstenalogaController()
        rezultat_vrste = conn_pretraga.read()

        count_vrste = 0

        for record in rezultat_vrste:

            if count_vrste % 2 == 0:
                self.my_tree_vrsta_naloga.insert(parent='', index='end', iid=record[0], text='',
                                            values=(record[1],),
                                            tags=('evenrow',))
            else:
                self.my_tree_vrsta_naloga.insert(parent='', index='end', iid=record[0], text='',
                                            values=(record[1],),
                                            tags=('oddrow',))
            count_vrste += 1

    # Unos nove vrste dokumenta
    def unos_vrste_dokumenta(self):
        nova_vrsta_dokumenta = self.naziv_entry_nalog.get()

        # Provera da li su polja za unos prazna
        if (nova_vrsta_dokumenta == ''):
            messagebox.showwarning("Greška", "Morate uneti naziv naloga!", parent=self.prozor_vrste_naloga)
        else:
            conn = VrstenalogaController()
            conn.insert_nalog(nova_vrsta_dokumenta)
            # Brisanje entry polja nakon azuriranja vrste naloga
            self.ocisti_polje()
            # Brisanje tabele zbog azuriranja nove vrste naloga
            self.my_tree_vrsta_naloga.delete(*self.my_tree_vrsta_naloga.get_children())
            # povezivanje na bazu i prikaz u tabeli
            self.sve_vrste_naloga()

    def izaberi_red_nalog(self, e):
        # Prvo isprazniti polja
        self.naziv_entry_nalog.delete(0, 'end')
        # Uzeti identifikator reda
        selected = self.my_tree_vrsta_naloga.focus()
        # Uzamanje vrednosti iz izabranog reda
        # Mora ovaj try exept jer selektuje i header tabele, a onda vraća grešku out of range
        try:
            values_nalog = self.my_tree_vrsta_naloga.item(selected, 'values')
            # Prikaz vrednosti u entry poljima
            self.naziv_entry_nalog.insert(0, values_nalog[0])
        except IndexError:
            pass

    def ocisti_polje(self):
        self.naziv_entry_nalog.delete(0, 'end')

    # Izmena vrste naloga
    def izmeni_vrstu_naloga(self):
        # Uzeti identifikator reda
        selected = self.my_tree_vrsta_naloga.focus()
        if selected:
            promenjen_naziv_vrste_naloga = self.naziv_entry_nalog.get()
            self.my_tree_vrsta_naloga.item(selected, values=(promenjen_naziv_vrste_naloga,), )

            # povezivanje na bazu i preuzimanje vrste naloga iz tabele
            conn = VrstenalogaController()
            conn.update_nalog(promenjen_naziv_vrste_naloga, selected)

            # Brisanje entry polja nakon azuriranja vrste naloga
            self.ocisti_polje()
            # Brisanje tabele zbog azuriranja nove vrste naloga
            self.my_tree_vrsta_naloga.delete(*self.my_tree_vrsta_naloga.get_children())
            # povezivanje na bazu i prikaz u tabeli
            self.sve_vrste_naloga()
        else:
            messagebox.showinfo("Greska", "Hmmmm, niste odabrali ni jednu vrstu naloga!!", parent=self.prozor_vrste_naloga)

    # Brisanje konta
    def obrisi_vrstu_naloga(self):
        # Brisanje iz tabele treeview
        selected = self.my_tree_vrsta_naloga.focus()
        if selected:
            x = self.my_tree_vrsta_naloga.selection()[0]
            # Prvo proveriti da li ovaj nalog vec postoji u bazi i proknjizen

            # Brisanje iz baze podataka
            try:
                conn = VrstenalogaController()
                conn.delete_nalog(selected)
                self.my_tree_vrsta_naloga.delete(x)
                # Brisanje entry polja nakon brisanja konta
                self.ocisti_polje()
                # Brisanje tabele zbog azuriranja nove vrste naloga
                self.my_tree_vrsta_naloga.delete(*self.my_tree_vrsta_naloga.get_children())
                # povezivanje na bazu i prikaz u tabeli
                self.sve_vrste_naloga()
                # Pop up sa porukom o obrisanom kontu

                messagebox.showinfo("Obrisano", "Odabrana vrsta naloga je obrisana!", parent=self.prozor_vrste_naloga)

            except:
                messagebox.showinfo("Greska", "Hmmmm, neka greška prilikom povezivanja na bazu podataka!!", parent=self.prozor_vrste_naloga)

        else:
            messagebox.showinfo("Greska", "Hmmmm, niste odabrali ni jednu vrstu naloga!!", parent=self.prozor_vrste_naloga)

    def __init__(self):
        self.prozor_vrste_naloga = Toplevel()
        self.prozor_vrste_naloga.grab_set()
        self.prozor_vrste_naloga.title("Pregled i unos vrsta naloga")
        self.prozor_vrste_naloga.geometry("500x500")
        self.prozor_vrste_naloga.resizable(0, 0)
        self.prozor_vrste_naloga.columnconfigure(0, weight=1)
        self.prozor_vrste_naloga.rowconfigure(0, weight=1)
        self.prozor_vrste_naloga.rowconfigure(1, weight=4)
        self.prozor_vrste_naloga.rowconfigure(2, weight=3)

        # Prvi frame za spisak svih vrsta naloga - tabela
        self.list_sve_vrste_naloga = Frame(self.prozor_vrste_naloga)
        self.list_sve_vrste_naloga.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.list_sve_vrste_naloga.columnconfigure(0, weight=1)
        # list_sve_vrste_naloga.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_vrste_naloga = Canvas(self.list_sve_vrste_naloga)
        self.canvas_vrste_naloga.grid(row=0, column=0, sticky='nsew')
        self.canvas_vrste_naloga.columnconfigure(0, weight=1)
        # canvas_vrste_naloga.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                        fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])

        # Kreiranje canvasa za tabelu jer ne moze scroll bar da ide na Frame ili LabelFrame
        self.my_tree_vrsta_naloga = ttk.Treeview(self.canvas_vrste_naloga)
        self.my_tree_vrsta_naloga.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.my_tree_vrsta_naloga['columns'] = ("Naziv")
        self.my_tree_vrsta_naloga.column("#0", width=0, stretch=False)
        self.my_tree_vrsta_naloga.column("Naziv", anchor=tk.CENTER, minwidth=120)

        # Kreiranje vertikalnog scroll bara za tabelu
        self.treeVrstaScroll = ttk.Scrollbar(self.canvas_vrste_naloga)
        self.treeVrstaScroll.grid(row=0, column=1, sticky='ns')
        self.treeVrstaScroll.configure(command=self.my_tree_vrsta_naloga.yview)
        self.my_tree_vrsta_naloga.configure(yscrollcommand=self.treeVrstaScroll.set)

        self.my_tree_vrsta_naloga.heading("#0", anchor=tk.W, text="")
        self.my_tree_vrsta_naloga.heading("Naziv", anchor=tk.CENTER, text="Naziv")

        # Odredjivanje boje u redovima tabele - bela i plava, parni i neparni red
        self.my_tree_vrsta_naloga.tag_configure('oddrow', background="white")
        self.my_tree_vrsta_naloga.tag_configure('evenrow', background="lightblue")

        # Prikaz svih vrsta naloga u tabeli
        self.sve_vrste_naloga()

        # Drugi frame za entry polje naziv
        self.entry_polja_nalog = LabelFrame(self.prozor_vrste_naloga, text="Unos")
        self.entry_polja_nalog.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.entry_polja_nalog.columnconfigure(0, weight=1)
        self.entry_polja_nalog.columnconfigure(1, weight=3)
        self.entry_polja_nalog.rowconfigure(0, weight=1)

        # Label i polje za unos naziva naloga
        self.naziv_label_nalog = Label(self.entry_polja_nalog, text="Naziv vrste naloga:")
        self.naziv_label_nalog.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.naziv_entry_nalog = Entry(self.entry_polja_nalog)
        self.naziv_entry_nalog.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        self.naziv_entry_nalog.bind("<KeyRelease>", self.__proveri_jezik)


        # Treci frame za dugmad Dodaj, Izmeni, Obrisi i Izaberi
        self.polje_dugmad_nalog = LabelFrame(self.prozor_vrste_naloga, text="Komande", bg="lightblue")
        self.polje_dugmad_nalog.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.polje_dugmad_nalog.rowconfigure(0, weight=1)
        self.polje_dugmad_nalog.columnconfigure(0, weight=1)
        self.polje_dugmad_nalog.columnconfigure(1, weight=1)
        self.polje_dugmad_nalog.columnconfigure(2, weight=1)
        self.polje_dugmad_nalog.columnconfigure(3, weight=1)

        self.dugme_dodaj_nalog = Button(self.polje_dugmad_nalog, text="Dodaj nalog", bg='#40A2D8', fg='white', command=self.unos_vrste_dokumenta)
        self.dugme_dodaj_nalog.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        #self.dugme_dodaj_nalog.bind("<Return>", self.__proveri_jezik, add='+')
        #self.dugme_dodaj_nalog.bind("<ButtonRelease>", self.__proveri_jezik, add='+')

        self.dugme_izmeni_nalog = Button(self.polje_dugmad_nalog, text="Izmeni nalog", bg="#265073", fg="white", command=self.izmeni_vrstu_naloga)
        self.dugme_izmeni_nalog.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        #self.dugme_izmeni_nalog.bind("<Return>", self.__proveri_jezik, add='+')
        #self.dugme_izmeni_nalog.bind("<ButtonRelease-1>", self.__proveri_jezik, add='+')

        self.dugme_obrisi_nalog = Button(self.polje_dugmad_nalog, text="Obriši nalog", bg="#FF6868", fg="white", command=self.obrisi_vrstu_naloga)
        self.dugme_obrisi_nalog.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        self.dugme_izaberi_nalog = Button(self.polje_dugmad_nalog, text="Očisti polja za unos", command=self.ocisti_polje)
        self.dugme_izaberi_nalog.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        # Selektovanje reda iz tabele klikom na slog
        self.my_tree_vrsta_naloga.bind("<ButtonRelease-1>", self.izaberi_red_nalog)
