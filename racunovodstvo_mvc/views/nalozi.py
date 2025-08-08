from tkinter import ttk, Label, Frame, StringVar, Button, LabelFrame, Entry, Canvas, Toplevel, messagebox
import tkinter as tk
from tkinter import filedialog as fd
from racunovodstvo_mvc.controllers.VrstenalogaController import VrstenalogaController
from racunovodstvo_mvc.controllers.NaloziController import NaloziController
from racunovodstvo_mvc.controllers.AplikacijaController import AplikacijaController
from racunovodstvo_mvc.controllers.IzvoriController import IzvoriController
from racunovodstvo_mvc.controllers.KreiranNalogController import KreiranNalogController
from racunovodstvo_mvc.views.stampa_izvestaja import StampaIzvestaja
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.controllers.KeyboardController import KeyboardController
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.DimenzijeProzora import DimenzijeProzora
from racunovodstvo_mvc.controllers.DobavljacController import DobavljacController
from racunovodstvo_mvc.controllers.EfakturaController import EfakturaController
from tkcalendar import DateEntry
from datetime import date
import webbrowser
import xml.etree.ElementTree as ET
from mysql.connector import Error
from PyPDF2 import PdfMerger
from io import BytesIO
import base64
import random
import locale
import os
import shutil
import cyrtranslit


# Polje za unos i pregled naloga
class Nalozi:
    def __init__(self, master):
        self.master = master
        self.aktivna_godina = None
        self.id_naloga = None
        self.datum_naloga = None
        self.broj_naloga = None
        self.da_ne_proknjizen_nalog = None
        self.broj_kreiranog_naloga = None
        self.prozor_unos_naloga = None
        self.prozor_brisanje = None
        self.prvi_frame_naslov = None
        self.broj_naloga_label = None
        self.datum_naloga_label = None
        self.proknjizen_nalog_label = None
        self.proknjizen_nalog = None
        self.drugi_frame_unos = None
        self.konto_label = None
        self.izabran_konto_label1 = None
        self.izvor_label = None
        self.izabran_izvor_label1 = None
        self.duguje_label = None
        self.potrazuje_label = None
        self.konta_subanalitika_lista = None
        self.konto_entry_nalog = None
        self.izabran_konto_label = None
        self.izvor_combo = None
        self.izabran_izvor_label = None
        self.duguje_entry_nalog = None
        self.potrazuje_entry_nalog = None
        self.komentar_label = None
        self.komentar_entry_nalog = None
        self.dugme_dodaj_red = None
        self.dugme_izmeni_red = None
        self.dugme_obrisi_red = None
        self.dugme_izaberi_red = None
        self.treci_frame_unos = None
        self.canvas_tabela_nalog = None
        self.style = None
        self.tree_tabela_nalog = None
        self.treeScroll = None
        self.cetvrti_frame_unos = None
        self.saldo_duguje_text = None
        self.saldo_unos_duguje = None
        self.saldo_potrazuje_text = None
        self.saldo_unos_potrazuje = None
        self.peti_frame_unos = None
        self.dugme_proknjizi = None
        self.dugme_stampa = None
        self.nalozi_frame = None
        self.unos_naloga = None
        self.label_vrsta_naloga = None
        self.izaberi_vrstu_naloga = None
        self.vrsta_naloga_combo = None
        self.label_broj_naloga = None
        self.broj_novog_naloga = None
        self.broj_naloga = None
        self.label_datum_naloga = None
        self.datum_novog_naloga = None
        self.kreiraj_nalog_dugme = None
        self.pregled_naloga = None
        self.canvas_pregled_naloga = None
        self.my_tree = None
        self.buttons_frame = None
        self.dugme_pregledaj = None
        self.dugme_obrisi = None
        self.unesi_efakture = None
        self.pregledaj_efakture = None
        self.prozor_ucitane_efakture = None
        self.list_sve_efakture = None
        self.canvas_pregled_svih_efaktura = None
        self.my_tree_efakture = None
        self.style_efakture = None
        self.treeEfaktureScroll = None
        self.polje_dugmad_efakture = None
        self.dugme_otvori_efakturu = None
        self.dugme_obrisi_efakturu = None
        self.ukupan_saldo_text = None
        self.ukupan_saldo = None

    def __proveri_jezik_broj_naloga(self, event):
        ucitaj_kontrolu = KeyboardController()
        if ucitaj_kontrolu.check_language():
            messagebox.showwarning("Greška", "U polju 'Broj naloga' možete koristiti samo latinična slova!!", parent=self.master)
            self.broj_naloga.delete(0, 'end')

    # Provera koja tastatura se koristi za unos, ako je cirilica vratiti upozorenje, jer mogu samo da se unose latinicna slova- zbog stampe PDF
    def __proveri_jezik_komentar(self, event):
        if self.komentar_entry_nalog.get() != '':
            ucitaj_kontrolu = KeyboardController()
            if ucitaj_kontrolu.check_language():
                messagebox.showwarning("Greška", "Za unos komentara koristite latinična slova!!",
                                       parent=self.prozor_unos_naloga)
                self.komentar_entry_nalog.delete(0, 'end')

    def prozor_za_brisanje(self, pronadjen_nalog):
        self.prozor_brisanje = Toplevel(self.master)
        self.prozor_brisanje.rowconfigure(0, weight=1)
        self.prozor_brisanje.rowconfigure(1, weight=1)
        self.prozor_brisanje.columnconfigure(0, weight=1)
        self.prozor_brisanje.columnconfigure(1, weight=1)
        window_height = 120
        window_width = 250
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.prozor_brisanje.geometry(
            "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_brisanje.title("Brisanje naloga")
        self.prozor_brisanje.resizable(None, None)
        self.prozor_brisanje.grab_set()

        pitanje_label = Label(self.prozor_brisanje, text="Da li ste sigurni?")
        pitanje_label.grid(row=0, column=0, pady=20, sticky='nsew', columnspan=2)
        dugme_da = Button(self.prozor_brisanje, text='Da', bg='lightblue',
                          command=lambda: self.obrisi_nalog(pronadjen_nalog))
        dugme_da.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        dugme_odustani = Button(self.prozor_brisanje, text='Ne', bg='white', command=self.prozor_brisanje.destroy)
        dugme_odustani.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)

    def poruka_brisanje(self):
        # Pronalazenje ID naloga na osnovu klika
        selected = self.my_tree.focus()
        # x = self.my_tree.selection()[0]
        if selected:
            # Pronadji nalog po ID-u
            conn_pronadji = NaloziController()
            pronadjen_nalog = conn_pronadji.find_nalog(selected)

            # Provera da li je proknjizen nalog, ako je proknjizen nema brisanja
            if pronadjen_nalog[0][3] == 'da':
                messagebox.showwarning("Upozorenje.", "Ne možete da obrišete proknjižen nalog.", parent=self.master)
            else:
                self.prozor_za_brisanje(pronadjen_nalog)
        else:
            messagebox.showwarning("Greška", "Hmmmmm, niste izabrali ni jedan nalog!", parent=self.master)

    def ucitane_vrste_naloga(self):
        # povezivanje na bazu i preuzimanje vrsta naloga iz tabele
        conn = VrstenalogaController()
        rezultat_vrste = conn.read()
        sve_vrste_naloga = []
        for i in rezultat_vrste:
            sve_vrste_naloga.append(i[1])
        self.vrsta_naloga_combo['values'] = sve_vrste_naloga
        self.vrsta_naloga_combo['state'] = 'readonly'
        self.vrsta_naloga_combo.current(0)

    def svi_nalozi(self, aktivna_godina):
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog
        self.my_tree.delete(*self.my_tree.get_children())
        # Pronalazenje godine koja je aktivna - trenutna godina na vrhu ekrana
        self.aktivna_godina = aktivna_godina
        conn_nalozi = NaloziController()
        data = conn_nalozi.read(self.aktivna_godina)

        self.my_tree.tag_configure('oddrow', background="white")
        self.my_tree.tag_configure('evenrow', background="lightblue")
        self.my_tree.tag_configure('neproknjizen', background="#ffcbcb")

        count_nalozi_glavni_prozor = 1
        for record in data:
            if count_nalozi_glavni_prozor % 2 == 0:
                if record[4] == 'da':
                    self.my_tree.insert(parent='', index='end', iid=record[0], text='', values=(
                                    count_nalozi_glavni_prozor, record[3], record[1], record[2].strftime("%d.%m.%Y"), record[4]),
                                    tags=('evenrow',))
                else:
                    self.my_tree.insert(parent='', index='end', iid=record[0], text='', values=(
                        count_nalozi_glavni_prozor, record[3], record[1], record[2].strftime("%d.%m.%Y"), record[4]),
                                        tags=('neproknjizen',))
            else:
                if record[4] == 'da':
                    self.my_tree.insert(parent='', index='end', iid=record[0], text='', values=(
                                    count_nalozi_glavni_prozor, record[3], record[1], record[2].strftime("%d.%m.%Y"), record[4]),
                                    tags=('oddrow',))
                else:
                    self.my_tree.insert(parent='', index='end', iid=record[0], text='', values=(
                        count_nalozi_glavni_prozor, record[3], record[1], record[2].strftime("%d.%m.%Y"), record[4]),
                                        tags=('neproknjizen',))
            count_nalozi_glavni_prozor += 1

    # Pomocna funkcija za funkciju Kreiraj nalog
    def unos_naloga_u_bazu(self, datum_naloga_baza, izabran_broj_upper, izabrana_vrsta, otvaranje_pocetnog_stanja):
        proknjizen = 'ne'  # kada se tek formira nalog onda je neproknjizen
        # Pretraga sifre korisnika da se unese tu tabelu nalozi
        conn_korisnik = AplikacijaController()
        sifra_korisnika = conn_korisnik.find()[0][1]

        # Kreiranje naloga
        try:
            conn_unesi = KreiranNalogController()
            conn_unesi.insert_nalog(datum_naloga_baza, izabran_broj_upper, proknjizen, izabrana_vrsta, sifra_korisnika)
            # Obrisi entry polja za nalog na glavnoj stranici
            if otvaranje_pocetnog_stanja == 'ne':
                self.vrsta_naloga_combo.set('')
                self.broj_naloga.delete(0, 'end')
                # self.datum_novog_naloga.delete(0, 'end')
        except ValueError:
            messagebox.showwarning("Hmmmm", "Neka greška prilikom kreiranja novog naloga u bazi podataka!", parent=self.master)

    # Pomocna funkcija za funkciju Kreiraj nalog
    def otvaranje_novog_prozora_kreiran_nalog(self):
        try:
            # Pronalazenje u bazi naloga sa unetim brojem i preuzimanje podataka za prikaz: broj naloga, datum, proknjizen, id naloga
            conn_pronadji = NaloziController()
            pronadjen_nalog = conn_pronadji.pronadji_poslednji()  # nalog
            id_naloga = pronadjen_nalog[0][0]
            datum_naloga = pronadjen_nalog[0][1].strftime("%d.%m.%Y")
            broj_naloga = pronadjen_nalog[0][2]
            da_ne_proknjizen_nalog = pronadjen_nalog[0][3].capitalize()
            godina_naloga = datum_naloga[-4:]
            # Ponovno ucitavanje tabele na pocetnom ekranu da bi se video i ovaj novi nalog
            self.svi_nalozi(godina_naloga)
            self.kreiran_nalog(id_naloga, datum_naloga, broj_naloga, da_ne_proknjizen_nalog)
        except ValueError:
            messagebox.showwarning("Hmmmmm. Nešto nije u redu sa unosom novog naloga! Pokušajte ponovno.", parent=self.master)

    # Prozor za unos naloga
    def kreiraj_nalog(self):
        # Uzeti podatke: vrsta naloga, naziv naloga i datum naloga
        izabrana_vrsta = self.izaberi_vrstu_naloga.get()
        izabran_broj = self.broj_novog_naloga.get()
        izabran_datum = self.datum_novog_naloga.get_date()
        izabran_broj_upper = izabran_broj.upper()  # u bazu se upisuju velika slova zbog pretrage - da ne bude zabune mala ili velika slova kada se pretrazuje
        godina_naloga = izabran_datum.year
        otvaranje_pocetnog_stanja = 'ne'  # ovo mora da bi se razlikovalo redovno kreiranje naloga od otvaranja pocetnog stanja na pocetku godine

        # Provera da li su popunjena sva tri polja za nalog
        if len(str(izabran_datum)) == 0 or len(izabrana_vrsta) == 0 or len(izabran_broj) == 0:
            messagebox.showwarning("Greška", "Morate popuniti sva tri polja!", parent=self.master)
        else:
            # Konvertovanje datuma koji je u stringu u datetime format koji ide u bazu podataka
            # datum_naloga_baza = datetime.strptime(izabran_datum, "%d.%m.%Y.").date()
            datum_naloga_baza = izabran_datum
            conn = NaloziController()
            postoji = conn.check_nalog_exist(str(izabran_broj_upper), datum_naloga_baza.year)
            # Provera da li se datum naloga i datum aktivne godine slazu, ako ne, ne moze da se kreira nalog
            if str(godina_naloga) != str(self.aktivna_godina):
                messagebox.showwarning("Greška",
                                       "Datum naloga nije u istoj godini kao i aktivna godina koja je prikazana na vrhu ekrana.",
                                       parent=self.master)
            # Provera da li postoji broj naloga u tabeli nalozi - ne smeju da postoje dva ista broja
            elif postoji:
                messagebox.showwarning("Greška", "Već postoji nalog sa ovim brojem u ovoj godini!", parent=self.master)
            else:
                # Unos naloga u bazu
                self.unos_naloga_u_bazu(datum_naloga_baza, izabran_broj_upper, izabrana_vrsta, otvaranje_pocetnog_stanja)
                # Otvaranje novog prozora sa kreiranim nalogom za unos stavki naloga i azuriranje liste naloga na pocetnom ekranu
                self.otvaranje_novog_prozora_kreiran_nalog()

    def obrisi_nalog(self, pronadjen_nalog):
        # proveriti u tabeli efakture da li ima ovaj id naloga
        efaktura_conn = EfakturaController()
        pronadjene_efakture = efaktura_conn.find_efakture(pronadjen_nalog[0][0])
        if len(pronadjene_efakture) > 0:
            # ako ima nalog u tabeli efakture - obrisati te stavke
            for efaktura in pronadjene_efakture:
                efaktura_conn.delete_efakture(efaktura[0])
            # obrisati fajl efakture u direktorijumu
            destinacija = os.getcwd() + "\\efakture\\" + pronadjene_efakture[0][1]
            if os.path.exists(destinacija):
                os.remove(destinacija)
            else:
                pass
        # ako nema - ici dalje
        # Provera da li u nalogu postoje stavke naloga
        provera_stavke = StavkaNalogaController()
        broj_stavki_u_nalogu = provera_stavke.koliko_stavki(pronadjen_nalog[0][0])
        conn_pronadji = NaloziController()
        if broj_stavki_u_nalogu[0][0] > 0:
            # Pronadji sve stavke iz ovog naloga
            pronadjene_stavke = provera_stavke.find_stavke(pronadjen_nalog[0][0])
            for record in pronadjene_stavke:
                provera_stavke.delete_stavka(record[0])
            # Obrisi nalog
            try:
                conn_pronadji.delete_nalog(pronadjen_nalog[0][0])
                # Ponovo učitati listu naloga da se ne bi prikazao obrisani nalog
                self.prozor_brisanje.destroy()
                messagebox.showinfo("Obrisano", "Odabrani nalog je obrisan!", parent=self.master)
                self.svi_nalozi(pronadjen_nalog[0][1].year)
            except Error as e:
                self.prozor_brisanje.destroy()
                messagebox.showwarning("Hmmmm neka greška", f"Ne može se obrisati ovaj nalog! Nazovi programera! Poruka greške: {e}", parent=self.master)
        else:
            # Obrisi nalog
            try:
                conn_pronadji.delete_nalog(pronadjen_nalog[0][0])
                # Ponovo učitati listu naloga da se ne bi prikazao obrisani nalog
                self.prozor_brisanje.destroy()
                messagebox.showinfo("Obrisano", "Odabrani nalog je obrisan!", parent=self.master)
                self.svi_nalozi(pronadjen_nalog[0][1].year)
            except Error as e:
                self.prozor_brisanje.destroy()
                messagebox.showwarning("Hmmmm neka greška", f"Ne može se obrisati ovaj nalog! Nazovi programera! Poruka greške: {e}",
                                       parent=self.master)

    def pregledaj_nalog(self):
        # Pronalazenje ID naloga na osnovu klika
        selected = self.my_tree.focus()
        # Pronadji nalog po ID-u
        if selected:
            conn_pronadji = NaloziController()
            pronadjen_nalog = conn_pronadji.find_nalog(selected)
            # Otvaranje prozora naloga
            self.kreiran_nalog(pronadjen_nalog[0][0], pronadjen_nalog[0][1].strftime("%d.%m.%Y"), pronadjen_nalog[0][2], pronadjen_nalog[0][3])
        else:
            messagebox.showwarning("Greška", "Hmmmmm, niste izabrali ni jedan nalog!", parent=self.master)

    # Provera da li u poljima duguje i potrazuje su uneta slova - moraju samo brojevi, i pravljenje dva decimalna mesta
    def provera_broj_duguje(self, event=None):
        # propusta ako nije nista uneto da ne bi izlazila poruka
        if not self.duguje_entry_nalog.get() == '':
            # Konvertuje zarez u tacku, kod unosa brojeva duguje
            ucitan_broj = self.duguje_entry_nalog.get()
            promenjeno = ucitan_broj.replace(',', '.')
            # Overwrite the Entrybox content using the widget's own methods
            self.duguje_entry_nalog.delete(0, 'end')
            self.duguje_entry_nalog.insert(0, promenjeno)
            try:
                float(self.duguje_entry_nalog.get())
            except ValueError:
                self.duguje_entry_nalog.delete(0, 'end')
                messagebox.showwarning("Greska", "Morate uneti brojeve!!", parent=self.prozor_unos_naloga)
            else:
                # pravljenje dva decimalna mesta
                prom = float(self.duguje_entry_nalog.get())
                promenjen_broj = "{:.2f}".format(prom)
                self.duguje_entry_nalog.delete(0, 'end')
                self.duguje_entry_nalog.insert(0, promenjen_broj)

    def provera_broj_potrazuje(self, event=None):
        # propušta ako nije nista uneto da ne bi izlazila poruka
        if not self.potrazuje_entry_nalog.get() == '':
            # Konvertuje zarez u tacku, kod unosa brojeva potrazuje
            ucitan_broj = self.potrazuje_entry_nalog.get()
            promenjeno = ucitan_broj.replace(',', '.')
            # Overwrite the Entrybox content using the widget's own methods
            self.potrazuje_entry_nalog.delete(0, 'end')
            self.potrazuje_entry_nalog.insert(0, promenjeno)
            try:
                float(self.potrazuje_entry_nalog.get())
            except ValueError:
                self.potrazuje_entry_nalog.delete(0, 'end')
                messagebox.showwarning("Greska", "Morate uneti brojeve!!", parent=self.prozor_unos_naloga)
            else:

                # pravljenje dva decimalna mesta
                prom = float(self.potrazuje_entry_nalog.get())
                promenjen_broj = "{:.2f}".format(prom)
                self.potrazuje_entry_nalog.delete(0, 'end')
                self.potrazuje_entry_nalog.insert(0, promenjen_broj)

    # Pomocna metoda za dobijanje liste subanalitickih konta iz baze podataka
    def lista_subanalitickih_konta(self):
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
                                   parent=self.prozor_unos_naloga)

    # Pomocna funkcija za dobijanje svih izvora finansiranja koja se nalaze u bazi, a prikazuju se u comboboxu izvori
    def lista_izvora_finansiranja(self):
        # povezivanje na bazu i preuzimanje izvora finansiranja iz tabele
        try:
            conn = IzvoriController()
            rezultat = conn.read()
            izvori = []
            for i in rezultat:
                izvori.append(i[1])
            return izvori
        except ValueError:
            messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom čitanja liste izvora finansiranja!!",
                                   parent=self.prozor_unos_naloga)

    # Prebacivanje fokusa na sledeci element sa comboboxa konta u zavisnosti da li je trosak ili nije
    def focus_next_window_combo(self, event):
        enter_na_combobox = self.konto_entry_nalog.get()
        # Provera da li je u comboboxu izabran konto iz padajuceg menija, ne dozvoljava da se unese neka druga vrednost
        if enter_na_combobox in self.konta_subanalitika_lista:
            self.izvor_combo['state'] = 'normal'
            # Stavljanje vrednosti konta u label koji se unosi u bazu podataka
            self.izabran_konto_label.config(text=enter_na_combobox)
            # Ako nije konto rashoda, onda polje izvora finansiranja postaje neaktvno
            if not (enter_na_combobox.startswith("4") or enter_na_combobox.startswith(
                    "5") or enter_na_combobox.startswith("6")):
                self.izvor_combo['state'] = 'disabled'
                self.izabran_izvor_label.config(text='')
            # Prelazak na enter na sledeci widget
            event.widget.tk_focusNext().focus()
            return "break"
        else:
            messagebox.showinfo("Greška", "Morate izabrati konto iz liste!", parent=self.prozor_unos_naloga)

    # Prelazak fokusa na sledeci entry
    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()

    def selektovanje_konta(self, e):
        self.izvor_combo['state'] = 'normal'
        izbor = self.konto_entry_nalog.get()
        self.izabran_konto_label.config(text=izbor)
        # Ako nije konto rashoda, onda polje izvora finansiranja postaje neaktvno
        if not (izbor.startswith("4") or izbor.startswith("5") or izbor.startswith("6")):
            self.izvor_combo['state'] = 'disabled'
            self.izabran_izvor_label.config(text='')

    def selektovanje_izvora(self, event):
        izabrano = self.izvor_combo.get()
        self.izabran_izvor_label.config(text=izabrano)
        event.widget.tk_focusNext().focus()

    # Smanjivanje liste konta u comboboxu na osnovu onoga sto kuca korisnik
    def check_input(self, event):
        value = event.widget.get()
        if value == '':
            self.konto_entry_nalog['values'] = self.konta_subanalitika_lista
        else:
            data = []
            for item in self.konta_subanalitika_lista:
                if value.lower() in item.lower():
                    data.append(item)

            self.konto_entry_nalog['values'] = data

    # Ocisti polja za novi unos
    def ocisti_polja_nalog(self):
        self.konto_entry_nalog.delete(0, 'end')
        self.izabran_konto_label['text'] = ''
        self.izabran_izvor_label['text'] = ''
        self.duguje_entry_nalog.delete(0, 'end')
        self.potrazuje_entry_nalog.delete(0, 'end')
        self.komentar_entry_nalog.delete(0, 'end')

    # Selektovanje izabranog reda u tabeli - Stavke naloga
    def selektuj_red(self, e):
        # Prvo isprazniti polja
        self.ocisti_polja_nalog()
        # Uzeti identifikator reda
        selected = self.tree_tabela_nalog.focus()
        # Uzamanje vrednosti iz izabranog reda
        # Mora ovaj try exept jer selektuje i header tabele, a onda vraća grešku out of range
        try:
            values = self.tree_tabela_nalog.item(selected, 'values')
            if values[2] == "":
                self.izvor_combo['state'] = 'disabled'
            else:
                self.izvor_combo['state'] = 'enabled'
            # ovo mora jer kada se selektuje red, duguje i potrazuje su stringovi, pa to predstavlja problem kod update - zato se moraju pretvoriti u float, a ako je prazno ostaje isto
            if values[3] != '':
                vrednost_duguje = float(values[3].replace('.', '').replace(',', '.'))
            else:
                vrednost_duguje = values[3]

            if values[4] != '':
                vrednost_potrazuje = float(values[4].replace('.', '').replace(',', '.'))
            else:
                vrednost_potrazuje = values[4]

            # Prikaz vrednosti u entry poljima
            self.izabran_konto_label.config(text=values[0])
            self.izabran_izvor_label.config(text=values[2])
            self.duguje_entry_nalog.insert(0, vrednost_duguje)
            self.potrazuje_entry_nalog.insert(0, vrednost_potrazuje)
            self.komentar_entry_nalog.insert(0, values[5])

        except IndexError:
            pass

    # Pomocna funkcija za odredjivanje gde ce u tabeli biti prikazan iznos duguje ili potrazuje
    def duguje_potrazuje_even(self, id_sloga, prvi_deo, drugi_deo, treci_deo, cetvrti_deo, peti_deo, sesti_deo):
        if peti_deo == 'd':
            self.tree_tabela_nalog.insert(parent='', index='end', iid=id_sloga, text='',
                                          values=(
                                              prvi_deo, drugi_deo, treci_deo, cetvrti_deo, '',
                                              sesti_deo),
                                          tags=('evenrow',))
        else:
            self.tree_tabela_nalog.insert(parent='', index='end', iid=id_sloga, text='',
                                          values=(
                                              prvi_deo, drugi_deo, treci_deo, '', cetvrti_deo,
                                              sesti_deo),
                                          tags=('evenrow',))

    # Pomocna funkcija za odredjivanje gde ce u tabeli biti prikazan iznos duguje ili potrazuje
    def duguje_potrazuje_odd(self, id_sloga, prvi_deo, drugi_deo, treci_deo, cetvrti_deo, peti_deo, sesti_deo):
        if peti_deo == 'd':
            self.tree_tabela_nalog.insert(parent='', index='end', iid=id_sloga, text='',
                                          values=(
                                              prvi_deo, drugi_deo, treci_deo, cetvrti_deo, '',
                                              sesti_deo),
                                          tags=('oddrow',))
        else:
            self.tree_tabela_nalog.insert(parent='', index='end', iid=id_sloga, text='',
                                          values=(
                                              prvi_deo, drugi_deo, treci_deo, '', cetvrti_deo,
                                              sesti_deo),
                                          tags=('oddrow',))

    # Pomocna funkcija za prikaz podataka u tabeli
    def prikaz_podataka_u_tabeli(self, rezultat_stavke):
        # Brisanje entry polja nakon azuriranja konta
        locale.setlocale(locale.LC_ALL, 'de_DE')
        self.ocisti_polja_nalog()
        self.konto_entry_nalog.focus()
        # Brisanje tabele zbog popunjavanja tabele podacima iza baze - sve stavke naloga za taj nalog
        self.tree_tabela_nalog.delete(*self.tree_tabela_nalog.get_children())
        # Pretraga baze za stavkama naloga
        # Ovde idu podaci iz stavki naloga i prikazuju se u tabeli

        self.tree_tabela_nalog.tag_configure('oddrow', background="white")
        self.tree_tabela_nalog.tag_configure('evenrow', background="lightblue")

        count_stavke_naloga = 0
        duguje = 0
        potrazuje = 0
        saldo = 0

        for record in rezultat_stavke:

            # Racunanje salda naloga duguje/potrazuje

            if record[5] == 'd':
                duguje += record[4]
            else:
                potrazuje += record[4]

            saldo = duguje - potrazuje
            iznos_za_prikaz = locale.format_string('%10.2f', record[4], grouping=True)

            # Prikaz u tabeli
            if count_stavke_naloga % 2 == 0:

                self.duguje_potrazuje_even(record[0], record[1], record[2], record[3], iznos_za_prikaz, record[5],
                                           record[6])

            else:
                self.duguje_potrazuje_odd(record[0], record[1], record[2], record[3], iznos_za_prikaz, record[5],
                                          record[6])

            count_stavke_naloga += 1
        # Ova komanda pomera scroll na kraj tabele da bi se videlo koji je poslednji slog unet (dobra stvar:)
        self.tree_tabela_nalog.yview_moveto(1)
        duguje_prikaz = locale.format_string('%10.2f', duguje, grouping=True)
        potrazuje_prikaz = locale.format_string('%10.2f', potrazuje, grouping=True)
        saldo_prikaz = locale.format_string('%10.2f', saldo, grouping=True)
        # Racunanje ukupno za nalog duguje ili potrazuje
        self.saldo_unos_duguje.config(text=duguje_prikaz)
        self.saldo_unos_potrazuje.config(text=potrazuje_prikaz)
        self.ukupan_saldo.config(text=saldo_prikaz)
        # Postavljanje kursora na polje combobox za unos konta
        self.konto_entry_nalog.focus_set()

        # Unos novog reda u Nalog

    def dodaj_red(self, e=None):
        self.provera_broj_duguje()
        self.provera_broj_potrazuje()
        izabran_konto = self.izabran_konto_label.cget("text")
        izabran_izvor = self.izabran_izvor_label.cget("text")
        izabran_duguje = self.duguje_entry_nalog.get()
        izabran_potrazuje = self.potrazuje_entry_nalog.get()
        izabran_komentar = self.komentar_entry_nalog.get()
        # provera da li je unet konto
        if izabran_konto == '':
            messagebox.showwarning("Greška", "Niste uneli konto!", parent=self.prozor_unos_naloga)
        else:
            # Dobijanje ID konta
            conn_konto = KontoController()
            pronadji_konto = conn_konto.find(izabran_konto)
            id_konta = pronadji_konto[0][0]

            # Odredjivanje iznosa stavke i da li duguje ili potrazuje
            if (izabran_duguje == "") and (izabran_potrazuje == ""):
                messagebox.showwarning("Greška", "Ne mogu obe vrednosti duguje i potražuje da budu prazne!",
                                       parent=self.prozor_unos_naloga)
            elif (izabran_duguje != "") and (izabran_potrazuje != ""):
                messagebox.showwarning("Greška", "Ne mogu da se unesu obe vrednosti duguje i potražuje!",
                                       parent=self.prozor_unos_naloga)
            else:
                # Uzimanje iznosa i odredjivanje da li je duguje ili potrazuje
                if izabran_duguje == "":
                    iznos = izabran_potrazuje
                    status_dp = "p"
                else:
                    iznos = izabran_duguje
                    status_dp = "d"
                iznos_za_unos = round(float(iznos), 2)
                try:
                    # Unos nove stavke u bazu
                    conn_unos = StavkaNalogaController()
                    conn_unos.insert_stavka(id_konta, izabran_izvor, self.id_naloga, iznos_za_unos, status_dp,
                                            izabran_komentar)
                    # Citanje stavki naloga iz baze i prikaz u tabeli, racunanje salda
                    rezultat_stavke = conn_unos.find_join(self.id_naloga)
                    self.prikaz_podataka_u_tabeli(rezultat_stavke)
                except ValueError:
                    messagebox.showinfo("Greška",
                                        "Hmmmmm nešto nije u redu sa bazom podataka, nije uspela izmena, pokušajte ponovo!",
                                        parent=self.prozor_unos_naloga)

        # Izmena unetog reda u tabeli - stavka naloga
    def izmeni_red(self):
        self.provera_broj_duguje()
        self.provera_broj_potrazuje()
        # Uzeti identifikator reda
        selected = self.tree_tabela_nalog.focus()
        if selected:
            # Prikaz vrednosti u entry poljima
            promenjen_konto = self.izabran_konto_label.cget("text")
            promenjen_izvor = self.izabran_izvor_label.cget("text")
            promenjen_duguje = self.duguje_entry_nalog.get()
            promenjen_potrazuje = self.potrazuje_entry_nalog.get()
            promenjen_komentar = self.komentar_entry_nalog.get()
            # Dobijanje ID konta
            conn_konto = KontoController()
            pronadji_konto = conn_konto.find(promenjen_konto)
            id_konta = pronadji_konto[0][0]

            # Uzimanje iznosa i odredjivanje da li je duguje ili potrazuje
            if promenjen_duguje == "":
                iznos = promenjen_potrazuje
                status_dp = "p"
            else:
                iznos = promenjen_duguje
                status_dp = "d"
            konvertuj_u_float = float(iznos)
            iznos_za_unos = round(konvertuj_u_float, 2)
            try:
                # povezivanje na bazu i azuriranje stavke naloga iz tabele
                conn = StavkaNalogaController()
                conn.update_stavka(id_konta, promenjen_izvor, iznos_za_unos, self.id_naloga, status_dp, promenjen_komentar,
                                   selected)
                # Citanje stavki naloga iz baze i prikaz u tabeli, racunanje salda
                rezultat_stavke = conn.find_join(self.id_naloga)
                self.prikaz_podataka_u_tabeli(rezultat_stavke)
            except ValueError:
                messagebox.showinfo("Greška",
                                    "Hmmmmm nešto nije u redu sa bazom podataka, nije uspela izmena, pokušajte ponovo!",
                                    parent=self.prozor_unos_naloga)
        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jedan red!", parent=self.prozor_unos_naloga)

        # Brisanje reda, jedne stavke naloga
    def obrisi_red(self):
        # Brisanje iz tabele treeview
        selected = self.tree_tabela_nalog.focus()
        if selected:
            x = self.tree_tabela_nalog.selection()[0]
            # Brisanje iz baze podataka
            try:
                conn_brisi = StavkaNalogaController()
                conn_brisi.delete_stavka(selected)
                self.tree_tabela_nalog.delete(x)
                # Citanje stavki naloga iz baze i prikaz u tabeli, racunanje salda
                rezultat_stavke = conn_brisi.find_join(self.id_naloga)
                self.prikaz_podataka_u_tabeli(rezultat_stavke)
                # Pop up sa porukom o obrisanoj stavki naloga
                messagebox.showinfo("Obrisano", "Odabrana stavka je obrisana!", parent=self.prozor_unos_naloga)

            except ValueError:
                messagebox.showwarning("Greska", "Hmmmm, neka greška prilikom brisanja stavke!! Pokušajte ponovo!",
                                       parent=self.prozor_unos_naloga)
        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jedan red!", parent=self.prozor_unos_naloga)

    # Knizenje naloga
    def proknjizi_nalog(self):
        # U sustini to je update naloga gde se polje proknjizen menja iz 'ne' u 'da', unosi se i datum knjizenja-danasnji datum
        nalog_id = self.id_naloga
        datum_knjizenja = date.today()
        proknjizen = 'da'
        # Pretraga sifre korisnika da se unese tu tabelu nalozi
        conn_korisnik = AplikacijaController()
        sifra_korisnika = conn_korisnik.find()[0][1]

        duguje = self.saldo_unos_duguje.cget("text")
        potrazuje = self.saldo_unos_potrazuje.cget("text")

        # Get last 4 character
        godina_naloga = self.datum_naloga[-4:]

        # Provera da li nalog ima stavke, ako nema stavke, prikazati obavestenje da je nalog prazan
        konekcija = StavkaNalogaController()
        koliko_stavki_ima_nalog = konekcija.koliko_stavki(nalog_id)

        if koliko_stavki_ima_nalog[0][0] == 0:
            messagebox.showwarning("Pažnja", "Nalog nema ni jednu stavku, ne možete da ga proknjižite!",
                                   parent=self.prozor_unos_naloga)
        else:
            # Provera da li je nalog u ravnotezi, odnosno da su duguje i potrazuje jednaki
            if duguje == potrazuje:
                try:
                    # Ako je ravnoteza, azuriraj nalog
                    conn_update = KreiranNalogController()
                    conn_update.update_nalog(nalog_id, proknjizen, datum_knjizenja, sifra_korisnika)

                    # Ponovo ucitaj listu (azuriranje) svih naloga iz izabrane godine na pocetnoj strani
                    self.svi_nalozi(godina_naloga)
                    # conn_update.svi_nalozi(godina_naloga)
                    messagebox.showinfo("Pronjiženo", "Nalog je proknjižen!", parent=self.prozor_unos_naloga)
                    self.proknjizen_nalog.config(text="Da")
                    self.dugme_proknjizi.config(state="disabled")
                    self.dugme_dodaj_red.config(state="disabled")
                    self.dugme_izmeni_red.config(state="disabled")
                    self.dugme_obrisi_red.config(state="disabled")
                    self.unesi_efakture.config(state="disabled")
                    self.dugme_stampa.config(state="normal")
                except ValueError:
                    messagebox.showwarning("Greška",
                                           "Hmmmm, neka greška prilikom knjizenja naloga!! Pokušajte ponovo!",
                                           parent=self.prozor_unos_naloga)
            else:
                messagebox.showwarning("Greška", "Nalog nije u ravnoteži!", parent=self.prozor_unos_naloga)

    def stampaj_nalog(self):
        conn = StavkaNalogaController()
        rezultat_stavke = conn.find_join(self.id_naloga)
        conn_pronadji_nalog = NaloziController()
        pronadjen_nalog = conn_pronadji_nalog.find_nalog(self.id_naloga)
        datum = pronadjen_nalog[0][5]
        datum_knjizenja = datum.strftime("%d.%m.%Y")

        try:
            stampanje = StampaIzvestaja()
            stampanje.stampa_naloga(rezultat_stavke, self.datum_naloga, self.broj_kreiranog_naloga, datum_knjizenja)
        except OSError:
            messagebox.showwarning("Greška", "Morate zatvoriti prethodni PDF izveštaj!", parent=self.prozor_unos_naloga)

    def convert_u_latinicu(self, tekst):
        return cyrtranslit.to_latin(tekst)

    def pronadji_broj_ugovora(self, root,  namespace):
        endpoint_id = root.find('.//cac:ContractDocumentReference/cbc:ID', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_broj_fakture(self, root, namespace):
        endpoint_id = root.find('.//cbc:ID', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_datum_izdavanja_efakture(self, root, namespace):
        endpoint_id = root.find('.//env:CreationDate', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_pib_dobavljaca(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingSupplierParty/cac:Party/cbc:EndpointID', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_naziv_dobavljaca(self, root, namespace):
        endpoint_id = root.find('.//cac:PartyLegalEntity/cbc:RegistrationName', namespace)
        if endpoint_id is not None:
            return self.convert_u_latinicu(endpoint_id.text)
        else:
            return None

    def pronadji_iznos_fakture(self, root, namespace):
        endpoint_id = root.find('.//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def unesi_dobavljaca_u_bazu(self, pib, naziv, id_konta):
        conn = DobavljacController()
        conn.unos_dobavljaca_u_tabelu(pib, naziv, id_konta)

    def pronadji_poslednji_slog_konto(self):
        conn = KontoController()
        return conn.pronadji_poslednji_konto()[0][0]

    def unesi_efakturu_u_bazu(self, naziv_fakture, id_naloga):
        conn_efakture = EfakturaController()
        conn_efakture.insert_efaktura(naziv_fakture, id_naloga)

    def knjizenje_dobavljaca_i_131211(self, id_konta_131211, id_naloga, iznos_fakture, id_konta_dobavljaca):
        try:
            # Unos nove stavke u bazu
            conn_unos = StavkaNalogaController()
            conn_unos.insert_stavka(id_konta_131211, "", id_naloga, iznos_fakture, "d", "")
            conn_unos.insert_stavka(id_konta_dobavljaca, "", self.id_naloga, iznos_fakture, "p", "")
            # Citanje stavki naloga iz baze i prikaz u tabeli, racunanje salda
            rezultat_stavke = conn_unos.find_join(id_naloga)
            self.prikaz_podataka_u_tabeli(rezultat_stavke)
        except ValueError:
            messagebox.showinfo("Greška",
                                "Hmmmmm nešto nije u redu sa bazom podataka, nije uspela izmena, pokušajte ponovo!",
                                parent=self.prozor_unos_naloga)

    def izaberi_efakture(self):
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        filetypes = (
            ('text files', '*.xml'),
        )
        izabrane_fakture = fd.askopenfilenames(
            parent=self.prozor_unos_naloga,
            title='Open files',
            initialdir=desktop,
            filetypes=filetypes)

        for faktura in izabrane_fakture:
            # izvlacenje naziva i ekstenzije fakture
            base = os.path.basename(faktura)
            # dodavanje random broja nazivu fakture, da se ne bi slucajno pojavile dve razlicite fakture sa istim brojem
            random_broj = str(random.randint(1, 1000000))
            #destinacija = os.getcwd() + "\\racunovodstvo_mvc\\efakture\\" + random_broj + "_" + base
            destinacija = os.getcwd() + "\\efakture\\" + random_broj + "_" + base
            naziv_efakture = random_broj + "_" + base
            # kopiranje fakture u folder efakture
            shutil.copy(faktura, destinacija)
            # ocitati xml
            tree = ET.parse(destinacija)
            root = tree.getroot()
            namespaces = {'env': 'urn:eFaktura:MinFinrs:envelop:schema', 'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2", 'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
            # pronaci PIB dobavljaca
            pib = self.pronadji_pib_dobavljaca(root, namespaces)
            if pib is not None:
                # pronaci ID konta 131211
                konto_conn = KontoController()
                pronadji_id_konta = konto_conn.find("131211")
                id_konta_131211 = pronadji_id_konta[0][0]
                # pronaci naziv dobavljaca
                naziv_dobavljaca = self.pronadji_naziv_dobavljaca(root, namespaces)[:40]
                #naziv_dobavljaca_latin = self.convert_u_latinicu(naziv_dobavljaca)
                # pronaci iznos fakture
                iznos_fakture = self.pronadji_iznos_fakture(root, namespaces)
                # proveriti u tabeli dobavljaca da li postoji
                conn_dob = DobavljacController()
                pronadjen_dobavljac = conn_dob.pronadji_dobavljaca(pib)
                if pronadjen_dobavljac[0][0] > 0:
                    # ako postoji - pronaci ID konta 252111 za tog dobavljaca
                    pronadjen_id_konta_dobavljaca = conn_dob.pronadji_dobavljaca_svi_podaci(pib)
                    id_konta_dobavljaca = pronadjen_id_konta_dobavljaca[0][3]
                    # proknizi dobavljaca i 131211
                    self.knjizenje_dobavljaca_i_131211(id_konta_131211, self.id_naloga, iznos_fakture, id_konta_dobavljaca)
                # ako ne postoji - uneti dobavljaca u tabelu i napraviti konto 252111 - dobavljac
                else:
                    # kreiranje novog konta 252111 sa unetim dobavljacem
                    if naziv_dobavljaca.isascii():
                        naziv_dobavljaca_upis_u_bazu = naziv_dobavljaca
                        novi_konto = "252111-" + naziv_dobavljaca
                        novi_naziv = 'Dobavljači u zemlji ' + naziv_dobavljaca
                    else:
                        naziv_dobavljaca_lat = self.convert_u_latinicu(naziv_dobavljaca)
                        naziv_dobavljaca_upis_u_bazu = naziv_dobavljaca_lat
                        novi_konto = "252111-" + naziv_dobavljaca_lat
                        novi_naziv = 'Dobavljači u zemlji ' + naziv_dobavljaca_lat
                    vrsta = 'subanalitika'
                    try:
                        conn = KontoController()
                        conn.insert_konto(novi_konto, novi_naziv, vrsta)
                        # self.lista_subanalitickih_konta()
                    except ValueError:
                        messagebox.showinfo("Greška", "Hmmmmm prilikom unosa dobavljača, pokušajte ponovo!",
                                            parent=self.prozor_unos_naloga)
                    # unos dobavljaca u tabelu dobavljaci
                    # pronadji poslednji red u tabeli konto da se dobije ID ovog konta
                    id_konta_dobavljaca = self.pronadji_poslednji_slog_konto()
                    try:
                        self.unesi_dobavljaca_u_bazu(pib, naziv_dobavljaca_upis_u_bazu, id_konta_dobavljaca)
                    except ValueError:
                        messagebox.showinfo("Greška", "Hmmmmm prilikom unosa dobavljača, pokušajte ponovo!",
                                            parent=self.prozor_unos_naloga)
                    # proknizi dobavljaca i 131211
                    self.knjizenje_dobavljaca_i_131211(id_konta_131211, self.id_naloga, iznos_fakture, id_konta_dobavljaca)
                # upisati efakturu u tabelu efakture - naziv.xml i id naloga
                try:
                    self.unesi_efakturu_u_bazu(naziv_efakture, self.id_naloga)
                except ValueError:
                    messagebox.showinfo("Greška", "Hmmmmm prilikom unosa eFakture!",
                                        parent=self.prozor_unos_naloga)
            else:
                messagebox.showwarning("Hmmmm", "Izgleda da nešto nije u redu sa eFakturom! Nisam je proknjižio, a ti proveri šta je u pitanju i unesi je ručno.", parent=self.prozor_unos_naloga)

    # Prikazuje u tabeli sve dobavljace
    def prikaz_efaktura_u_tabeli(self, rezultat):
        # global count_konto
        count_fakture = 0

        for record in rezultat:
            if count_fakture % 2 == 0:
                self.my_tree_efakture.insert(parent='', index='end', iid=record[0], text='',
                                               values=(record[1], locale.format_string('%10.2f', float(record[2]), grouping=True)),
                                               tags=('evenrow',))
            else:
                self.my_tree_efakture.insert(parent='', index='end', iid=record[0], text='',
                                               values=(record[1], locale.format_string('%10.2f', float(record[2]), grouping=True)),
                                               tags=('oddrow',))
            count_fakture += 1

    def prikaz_svih_efaktura(self):
        # pronaci efakture od izabranog naloga
        conn_efakture = EfakturaController()
        rezultat = conn_efakture.find_efakture(self.id_naloga)
        # ocitati svaku eFakturu i izvuci id, naziv dobavljaca i iznos fakture
        namespaces = {'env': 'urn:eFaktura:MinFinrs:envelop:schema', 'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2", 'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
        lista_efaktura = []
        if len(rezultat) > 0:
            for faktura in rezultat:
                naziv_fakture = faktura[1]
                # faktura_podaci = ()
                destinacija = self.folder_efaktura() + naziv_fakture
                if os.path.exists(destinacija):
                    # ocitati xml
                    tree = ET.parse(destinacija)
                    root = tree.getroot()
                    # pronaci naziv dobavljaca
                    naziv_dobavljaca = self.pronadji_naziv_dobavljaca(root, namespaces)
                    # pronaci iznos fakture
                    iznos_fakture = self.pronadji_iznos_fakture(root, namespaces)
                    faktura_podaci = (faktura[0], naziv_dobavljaca, iznos_fakture)
                    # napraviti listu
                    lista_efaktura.append(faktura_podaci)
                else:
                    messagebox.showinfo("Greška", "Hmmmmm nemate fakturu dobavljača u folderu eFakture! Naziv fajla koji nedostaje je: " + naziv_fakture,
                                        parent=self.prozor_ucitane_efakture)
            # uneti u tabelu
            self.prikaz_efaktura_u_tabeli(lista_efaktura)

    def folder_efaktura(self):
        return os.getcwd() + "\\efakture\\"

    def nadji_naziv_efakture(self, id_efakture):
        conn_efakture = EfakturaController()
        pronadjena_efaktura = conn_efakture.find_efakture_by_id(id_efakture)
        return pronadjena_efaktura[0][1]

    def obrisi_efakturu(self):
        # Uzeti identifikator reda
        selected = self.my_tree_efakture.focus()
        destinacija = self.folder_efaktura()
        if selected:
            # pronaci u tabeli efakture izabranu fakturu i obrisati je
            pronadjena_efaktura_naziv = self.nadji_naziv_efakture(selected)
            try:
                conn_efakture = EfakturaController()
                conn_efakture.delete_efakture(selected)
            except ValueError:
                messagebox.showinfo("Greška", "Hmmmmm neka greška prilikom brisanja eFakture!",
                                    parent=self.prozor_ucitane_efakture)
            # iz foldera efakture obrisati izabranu fakturu fizicki
            faktura_za_brisanje = destinacija + pronadjena_efaktura_naziv
            if os.path.exists(faktura_za_brisanje):
                os.remove(faktura_za_brisanje)
                # Brisanje tabele zbog azuriranja novog konta
                self.my_tree_efakture.delete(*self.my_tree_efakture.get_children())
                # povezivanje na bazu i prikaz u tabeli
                self.prikaz_svih_efaktura()
            else:
                messagebox.showinfo("Greška", "Ova eFaktura se ne nalazi u folderu! Nisam ni mogao da je obrišem!",
                                    parent=self.prozor_ucitane_efakture)
        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jednu eFakturu za brisanje!",
                                   parent=self.prozor_ucitane_efakture)

    def pronadji_mime_pdf(self, root, namespace):
        endpoint_id = root.find('.//env:DocumentPdf', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_priloge_efakture(self, root, namespace):
        embedded_objects = root.findall('.//cbc:EmbeddedDocumentBinaryObject', namespace)
        if embedded_objects is not None:
            lista_priloga = []
            for obj in embedded_objects:
                lista_priloga.append(obj.text)
            return lista_priloga
        else:
            return None
    '''
    def pronadji_datum_prometa(self, root, namespace):
        endpoint_id = root.find('.//cbc:IssueDate', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_datum_dospeca(self, root, namespace):
        endpoint_id = root.find('.//cbc:DueDate', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_jbkjs(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_maticni_broj_kupca(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID', namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_pib_kupca(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingCustomerParty/cac:Party/cbc:EndpointID',
                                namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_valutu_fakture(self, root, namespace):
        endpoint_id = root.find('.//cac:LegalMonetaryTotal/cbc:PayableAmount', namespace)
        if endpoint_id is not None:
            return endpoint_id.get('currencyID')
        else:
            return None

    def pronadji_iznos_za_placanje(self, root, namespace):
        endpoint_id = root.find('.//cac:LegalMonetaryTotal/cbc:PayableAmount',
                                namespace)
        if endpoint_id is not None:
            return endpoint_id.text
        else:
            return None

    def pronadji_naziv_kupca(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name',
                                namespace)
        if endpoint_id is not None:
            return self.convert_u_latinicu(endpoint_id.text)
        else:
            return None

    def pronadji_adresu_kupca(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:StreetName',
                                namespace)
        if endpoint_id is not None:
            return self.convert_u_latinicu(endpoint_id.text)
        else:
            return None

    def pronadji_grad_kupca(self, root, namespace):
        endpoint_id = root.find('.//cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cbc:CityName',
                                namespace)
        if endpoint_id is not None:
            return self.convert_u_latinicu(endpoint_id.text)
        else:
            return None
    '''
    def kreiraj_efakturu_za_stampu(self):
        # Uzeti identifikator reda
        selected = self.my_tree_efakture.focus()
        destinacija = self.folder_efaktura()
        if selected:
            # pronaci u tabeli efakture izabranu fakturu i obrisati je
            pronadjena_efaktura_naziv = self.nadji_naziv_efakture(selected)
            faktura_za_prikaz = destinacija + pronadjena_efaktura_naziv
            tree = ET.parse(faktura_za_prikaz)
            root = tree.getroot()
            namespaces = {'env': 'urn:eFaktura:MinFinrs:envelop:schema',
                          'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                          'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
            if os.path.exists(faktura_za_prikaz):

                base64_pdf_efaktura = self.pronadji_mime_pdf(root, namespaces)
                base64_pdf_prilozi = self.pronadji_priloge_efakture(root, namespaces)

                if base64_pdf_prilozi is not None:
                    # spoj efakturu sa prilozima
                    base64_pdf_prilozi.insert(0, base64_pdf_efaktura)
                    merger = PdfMerger()
                    # iteriranje kroz base64 objekte, dekodiranje i dodavanje u pdfMerger
                    for b64_obj in base64_pdf_prilozi:
                        pdf_data = base64.b64decode(b64_obj)
                        pdf_file = BytesIO(pdf_data)
                        merger.append(pdf_file)
                    # zapisivanje dekodiranih bajtova u PDF fajl
                    try:
                        with open('efaktura.pdf', 'wb') as f:
                            merger.write(f)
                            webbrowser.open_new(r'efaktura.pdf')
                    except OSError:
                        messagebox.showinfo("Greška", "Imate već otvorenu neku eFakturu! Morate prvo nju zatvoriti.",
                                            parent=self.prozor_ucitane_efakture)
                else:
                    # Dekodirajte Base64 string
                    pdf_bytes = base64.b64decode(base64_pdf_efaktura)
                    # Zapiši dekodirane bajtove u PDF fajl
                    try:
                        with open('efaktura.pdf', 'wb') as pdf_file:
                            pdf_file.write(pdf_bytes)
                        webbrowser.open_new(r'efaktura.pdf')
                    except OSError:
                        messagebox.showinfo("Greška", "Imate već otvorenu neku eFakturu! Morate prvo nju zatvoriti.",
                                            parent=self.prozor_ucitane_efakture)
            else:
                messagebox.showinfo("Greška", "Ova eFaktura se ne nalazi u folderu!",
                                    parent=self.prozor_ucitane_efakture)
        else:
            messagebox.showwarning("Greška", "Hmmmm niste odabrali ni jednu eFakturu!",
                                   parent=self.prozor_ucitane_efakture)

    def ucitane_efakture(self):
        self.prozor_ucitane_efakture = Toplevel()
        # self.prozor_ucitane_efakture.attributes('-topmost', 'true')
        self.prozor_ucitane_efakture.grab_set()
        self.prozor_ucitane_efakture.title("Pregled učitanih eFaktura za nalog: " + self.broj_kreiranog_naloga)
        self.prozor_ucitane_efakture.geometry("800x600")
        self.prozor_ucitane_efakture.resizable(0, 0)
        self.prozor_ucitane_efakture.columnconfigure(0, weight=1)
        self.prozor_ucitane_efakture.rowconfigure(0, weight=2)
        self.prozor_ucitane_efakture.rowconfigure(1, weight=1)

        # Prvi label frame - tabela sa spiskom dobavljaca
        self.list_sve_efakture = Frame(self.prozor_ucitane_efakture)
        self.list_sve_efakture.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.list_sve_efakture.columnconfigure(0, weight=1)
        self.list_sve_efakture.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_pregled_svih_efaktura = Canvas(self.list_sve_efakture)
        self.canvas_pregled_svih_efaktura.grid(row=0, column=0, sticky='nsew')
        self.canvas_pregled_svih_efaktura.columnconfigure(0, weight=1)
        self.canvas_pregled_svih_efaktura.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style_efakture = ttk.Style()
        self.style_efakture.theme_use('default')
        self.style_efakture.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                                        fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style_efakture.map('Treeview', background=[('selected', '#347083')])

        # Kreiranje canvasa za tabelu jer ne moze scroll bar da ide na Frame ili LabelFrame
        self.my_tree_efakture = ttk.Treeview(self.canvas_pregled_svih_efaktura)
        self.my_tree_efakture.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.my_tree_efakture['columns'] = ("Naziv", "Iznos")
        self.my_tree_efakture.column("#0", width=0, stretch=False)
        self.my_tree_efakture.column("Naziv", anchor=tk.W, minwidth=600)
        self.my_tree_efakture.column("Iznos", anchor=tk.E, minwidth=100)

        # Kreiranje vertikalnog scroll bara za tabelu
        self.treeEfaktureScroll = ttk.Scrollbar(self.canvas_pregled_svih_efaktura)
        self.treeEfaktureScroll.grid(row=0, column=1, sticky='ns')
        self.treeEfaktureScroll.configure(command=self.my_tree_efakture.yview)
        self.my_tree_efakture.configure(yscrollcommand=self.treeEfaktureScroll.set)

        self.my_tree_efakture.heading("#0", anchor=tk.W, text="")
        self.my_tree_efakture.heading("Naziv", anchor=tk.CENTER, text="Naziv")
        self.my_tree_efakture.heading("Iznos", anchor=tk.CENTER, text="Iznos")

        # Odredjivanje boje u redovima tabele - bela i plava, parni i neparni red
        self.my_tree_efakture.tag_configure('oddrow', background="white")
        self.my_tree_efakture.tag_configure('evenrow', background="lightblue")

        # *********** ovde ide prikaz tabele *******#
        self.prikaz_svih_efaktura()

        # drugi label frame - Komande
        self.polje_dugmad_efakture = LabelFrame(self.prozor_ucitane_efakture, text="Komande", bg="lightblue")
        self.polje_dugmad_efakture.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.polje_dugmad_efakture.rowconfigure(0, weight=1)
        self.polje_dugmad_efakture.columnconfigure(0, weight=1)
        self.polje_dugmad_efakture.columnconfigure(1, weight=1)
        self.polje_dugmad_efakture.columnconfigure(2, weight=1)
        self.polje_dugmad_efakture.columnconfigure(3, weight=1)
        self.polje_dugmad_efakture.columnconfigure(4, weight=1)

        self.dugme_otvori_efakturu = Button(self.polje_dugmad_efakture, text="Otvori eFakturu", bg='#40A2D8', fg='white', command=self.kreiraj_efakturu_za_stampu)
        self.dugme_otvori_efakturu.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.dugme_obrisi_efakturu = Button(self.polje_dugmad_efakture, text="Obriši eFakturu", bg="#FF6868", fg="white", command=self.obrisi_efakturu)
        self.dugme_obrisi_efakturu.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

    def kreiran_nalog(self, id_naloga, datum_naloga, broj_naloga, da_ne_proknjizen_nalog):
        self.prozor_unos_naloga = Toplevel(self.master)
        self.prozor_unos_naloga.title("Unos naloga")
        self.prozor_unos_naloga.resizable(False, False)
        self.prozor_unos_naloga.grab_set()
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        dimenzije = DimenzijeProzora(screen_width, screen_height)
        window_width = dimenzije.odredi_sirinu_kreiran_nalog()
        window_height = dimenzije.odredi_visinu_kreiran_nalog()

        screen_width = self.master.winfo_screenwidth()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = 0
        self.prozor_unos_naloga.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.prozor_unos_naloga.columnconfigure(0, weight=1)
        self.prozor_unos_naloga.rowconfigure(0, weight=1)
        self.prozor_unos_naloga.rowconfigure(1, weight=1)
        self.prozor_unos_naloga.rowconfigure(2, weight=3)
        self.prozor_unos_naloga.rowconfigure(3, weight=1)
        self.prozor_unos_naloga.rowconfigure(4, weight=1)

        self.id_naloga = id_naloga
        self.datum_naloga = datum_naloga
        self.broj_kreiranog_naloga = broj_naloga
        self.da_ne_proknjizen_nalog = da_ne_proknjizen_nalog
        #############################################################################################
        # Prvi frame broj i datum naloga
        self.prvi_frame_naslov = Frame(self.prozor_unos_naloga)
        self.prvi_frame_naslov.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        self.prvi_frame_naslov.columnconfigure(0, weight=1)
        self.prvi_frame_naslov.columnconfigure(1, weight=1)
        self.prvi_frame_naslov.rowconfigure(0, weight=1)
        self.prvi_frame_naslov.rowconfigure(1, weight=1)
        # Label - broj naloga
        self.broj_naloga_label = Label(self.prvi_frame_naslov, text=self.broj_kreiranog_naloga, font=(None, 12, 'bold'))
        self.broj_naloga_label.grid(row=0, column=0, padx=10, sticky='e')
        # Label - datum naloga
        self.datum_naloga_label = Label(self.prvi_frame_naslov, text=datum_naloga, font=(None, 12, 'bold'))
        self.datum_naloga_label.grid(row=0, column=1, padx=10, sticky='w')
        # Label - Da li je proknjizen nalog
        self.proknjizen_nalog_label = Label(self.prvi_frame_naslov, text='Proknjižen', font=(None, 10, 'bold'))
        self.proknjizen_nalog_label.grid(row=1, column=0, padx=10, sticky='e')
        # Label - DA/NE
        da_li_je_proknjizen = self.da_ne_proknjizen_nalog.capitalize()
        self.proknjizen_nalog = Label(self.prvi_frame_naslov, text=da_li_je_proknjizen, font=(None, 12, 'bold'))
        self.proknjizen_nalog.grid(row=1, column=1, padx=10, sticky='w')

        ##############################################################################################
        # Drugi frame unos konta, iznosa, komentara
        self.drugi_frame_unos = LabelFrame(self.prozor_unos_naloga, text="Unos", bg="lightblue")
        self.drugi_frame_unos.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.drugi_frame_unos.columnconfigure(0, weight=1)
        self.drugi_frame_unos.columnconfigure(1, weight=1)
        self.drugi_frame_unos.columnconfigure(2, weight=1)
        self.drugi_frame_unos.columnconfigure(3, weight=1)
        self.drugi_frame_unos.columnconfigure(4, weight=1)
        self.drugi_frame_unos.columnconfigure(5, weight=1)
        self.drugi_frame_unos.rowconfigure(0, weight=1)
        self.drugi_frame_unos.rowconfigure(1, weight=1)
        self.drugi_frame_unos.rowconfigure(2, weight=1)
        self.drugi_frame_unos.rowconfigure(3, weight=1)

        # Prvi red labele - oznake za entry polja
        self.konto_label = Label(self.drugi_frame_unos, text='Pronadji konto:', bg="lightblue")
        self.konto_label.grid(row=0, column=0, padx=10, sticky='nsew')

        self.izabran_konto_label1 = Label(self.drugi_frame_unos, text='Izabran konto:', font='bold', bg="lightblue")
        self.izabran_konto_label1.grid(row=0, column=1, padx=10, sticky='nsew')

        self.izvor_label = Label(self.drugi_frame_unos, text='Izvor:', bg="lightblue")
        self.izvor_label.grid(row=0, column=2, padx=10, sticky='nsew')

        self.izabran_izvor_label1 = Label(self.drugi_frame_unos, text='Izabran izvor', font='bold', bg="lightblue")
        self.izabran_izvor_label1.grid(row=0, column=3, padx=10, sticky='nsew')

        self.duguje_label = Label(self.drugi_frame_unos, text='Duguje:', bg="lightblue")
        self.duguje_label.grid(row=0, column=4, padx=10, sticky='nsew')

        self.potrazuje_label = Label(self.drugi_frame_unos, text='Potražuje:', bg="lightblue")
        self.potrazuje_label.grid(row=0, column=5, padx=10, sticky='nsew')

        # Drugi red entry polja
        # Dobijanje liste subanalitickih konta iz baze
        self.konta_subanalitika_lista = self.lista_subanalitickih_konta()
        self.konto_entry_nalog = ttk.Combobox(self.drugi_frame_unos, font="7", values=self.konta_subanalitika_lista)
        self.konto_entry_nalog.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.konto_entry_nalog.bind("<Return>", self.focus_next_window_combo)
        self.konto_entry_nalog.bind("<<ComboboxSelected>>", self.selektovanje_konta, add="+")
        self.konto_entry_nalog.bind("<KeyRelease>", self.check_input, add="+")

        self.izabran_konto_label = Label(self.drugi_frame_unos, width=20, wraplength=200, bg="lightblue")
        self.izabran_konto_label.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Uzimanje iz baze spisak izvora finansiranja

        svi_izvori = self.lista_izvora_finansiranja()
        self.izvor_combo = ttk.Combobox(self.drugi_frame_unos, justify='center', font="7", width="8")
        self.izvor_combo.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        self.izvor_combo['values'] = svi_izvori
        self.izvor_combo.current(0)
        self.izvor_combo.bind("<<ComboboxSelected>>", self.selektovanje_izvora)
        self.izvor_combo.bind("<Return>", self.selektovanje_izvora, add="+")

        self.izabran_izvor_label = Label(self.drugi_frame_unos, text='', bg="lightblue")
        self.izabran_izvor_label.grid(row=1, column=3, padx=10, pady=10, sticky='ew')

        self.duguje_entry_nalog = Entry(self.drugi_frame_unos, justify='right', font="7")
        self.duguje_entry_nalog.grid(row=1, column=4, padx=10, pady=10, sticky="ew")
        self.duguje_entry_nalog.bind("<Return>", self.focus_next_window, add="+")
        self.duguje_entry_nalog.bind("<Return>", self.provera_broj_duguje, add="+")
        self.duguje_entry_nalog.bind("<Leave>", self.provera_broj_duguje, add="+")

        self.potrazuje_entry_nalog = Entry(self.drugi_frame_unos, justify='right', font="7")
        self.potrazuje_entry_nalog.grid(row=1, column=5, padx=10, pady=10, sticky="ew")
        self.potrazuje_entry_nalog.bind("<Return>", self.focus_next_window)
        self.potrazuje_entry_nalog.bind("<Return>", self.provera_broj_potrazuje, add="+")
        self.potrazuje_entry_nalog.bind("<Leave>", self.provera_broj_potrazuje, add="+")

        self.komentar_label = Label(self.drugi_frame_unos, text='Komentar:', bg="lightblue")
        self.komentar_label.grid(row=2, column=0, padx=10, sticky='e')

        self.komentar_entry_nalog = Entry(self.drugi_frame_unos, font="7")
        self.komentar_entry_nalog.grid(row=2, column=1, columnspan=4, padx=10, pady=10, sticky="ew")
        self.komentar_entry_nalog.bind("<Return>", self.focus_next_window)
        self.komentar_entry_nalog.bind("<KeyRelease>", self.__proveri_jezik_komentar, add="+")

        # Ako je nalog proknjizen dugme za proknjizavanje postaje neaktivno, nema potrebe da se vise puta knjizi nalog
        if da_ne_proknjizen_nalog == "da":
            self.dugme_dodaj_red = Button(self.drugi_frame_unos, text="Dodaj red", state="disabled",
                                          command=self.dodaj_red)
        else:
            self.dugme_dodaj_red = Button(self.drugi_frame_unos, text="Dodaj red", bg='#40A2D8', fg='white', command=self.dodaj_red)
        self.dugme_dodaj_red.grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        self.dugme_dodaj_red.bind("<Return>", self.dodaj_red, add="+")

        # Ako je nalog proknjizen dugme za proknjizavanje postaje neaktivno, nema potrebe da se vise puta knjizi nalog
        if da_ne_proknjizen_nalog == "da":
            self.dugme_izmeni_red = Button(self.drugi_frame_unos, text="Izmeni red", state="disabled",
                                           command=self.izmeni_red)
        else:
            self.dugme_izmeni_red = Button(self.drugi_frame_unos, text="Izmeni red", bg="#265073", fg="white", command=self.izmeni_red)
        self.dugme_izmeni_red.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

        # Ako je nalog proknjizen dugme za proknjizavanje postaje neaktivno, nema potrebe da se vise puta knjizi nalog
        if da_ne_proknjizen_nalog == "da":
            self.dugme_obrisi_red = Button(self.drugi_frame_unos, text="Obriši red", state="disabled",
                                           command=self.obrisi_red)
        else:
            self.dugme_obrisi_red = Button(self.drugi_frame_unos, text="Obriši red", bg="#FF6868", fg="white", command=self.obrisi_red)
        self.dugme_obrisi_red.grid(row=3, column=2, padx=10, pady=10, sticky='ew')

        self.dugme_izaberi_red = Button(self.drugi_frame_unos, text="Očisti polja", command=self.ocisti_polja_nalog)
        self.dugme_izaberi_red.grid(row=3, column=3, padx=10, pady=10, sticky='ew')

        if da_ne_proknjizen_nalog == "da":
            self.unesi_efakture = Button(self.drugi_frame_unos, text='Unesi eFakture', bg="#E2DAD6", fg="black", state='disabled', command=self.izaberi_efakture)
        else:
            self.unesi_efakture = Button(self.drugi_frame_unos, text='Unesi eFakture', bg="#E2DAD6", fg="black", command=self.izaberi_efakture)
        self.unesi_efakture.grid(row=3, column=4, padx=10, pady=10, sticky='ew')
        # PRIKAZ I STAMPA EFAKTURA MORA DA SE RAZRADI - PROBLEM MI PRAVE AVANSNI RACUNI

        self.pregledaj_efakture = Button(self.drugi_frame_unos, text='Pregledaj eFakture', bg="#E2DAD6", fg="black", command=self.ucitane_efakture)
        self.pregledaj_efakture.grid(row=3, column=5, padx=10, pady=10, sticky='ew')

        ####################################################################################################
        # Treci frame TABELA
        # Definisanje polja za prikaz liste unetih i proknjizenih naloga
        self.treci_frame_unos = LabelFrame(self.prozor_unos_naloga, text="Nalog")
        self.treci_frame_unos.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.treci_frame_unos.columnconfigure(0, weight=1)
        self.treci_frame_unos.rowconfigure(0, weight=1)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_tabela_nalog = Canvas(self.treci_frame_unos)
        self.canvas_tabela_nalog.grid(row=0, column=0, sticky='nsew')
        self.canvas_tabela_nalog.columnconfigure(0, weight=1)
        self.canvas_tabela_nalog.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                             fieldbackground="d3d3d3")
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])
        self.tree_tabela_nalog = ttk.Treeview(self.canvas_tabela_nalog)
        self.tree_tabela_nalog.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.tree_tabela_nalog['columns'] = ("Konto", "Naziv konta", "Izvor", "Duguje", "Potrazuje", "Komentar")
        self.tree_tabela_nalog.column("#0", width=0, stretch=False)
        self.tree_tabela_nalog.column("Konto", anchor=tk.W, minwidth=100)
        self.tree_tabela_nalog.column("Naziv konta", anchor=tk.W, minwidth=130)
        self.tree_tabela_nalog.column("Izvor", anchor=tk.CENTER, width=40)
        self.tree_tabela_nalog.column("Duguje", anchor=tk.E, width=20)
        self.tree_tabela_nalog.column("Potrazuje", anchor=tk.E, width=20)
        self.tree_tabela_nalog.column("Komentar", anchor=tk.W, minwidth=200)

        self.treeScroll = ttk.Scrollbar(self.canvas_tabela_nalog)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.tree_tabela_nalog.yview)
        self.tree_tabela_nalog.configure(yscrollcommand=self.treeScroll.set)

        self.tree_tabela_nalog.heading("#0", anchor=tk.W, text="")
        self.tree_tabela_nalog.heading("Konto", anchor=tk.CENTER, text="Konto")
        self.tree_tabela_nalog.heading("Naziv konta", anchor=tk.CENTER, text="Naziv konta")
        self.tree_tabela_nalog.heading("Izvor", anchor=tk.CENTER, text="Izvor")
        self.tree_tabela_nalog.heading("Duguje", anchor=tk.CENTER, text="Duguje")
        self.tree_tabela_nalog.heading("Potrazuje", anchor=tk.CENTER, text="Potražuje")
        self.tree_tabela_nalog.heading("Komentar", anchor=tk.CENTER, text="Komentar")

        ##################################################################################################
        # Cetvrti frame polje za saldo duguje i potrazuje
        self.cetvrti_frame_unos = LabelFrame(self.prozor_unos_naloga, text="Saldo naloga")
        self.cetvrti_frame_unos.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')
        self.cetvrti_frame_unos.columnconfigure(0, weight=3)
        self.cetvrti_frame_unos.columnconfigure(1, weight=3)
        self.cetvrti_frame_unos.columnconfigure(2, weight=1)
        self.cetvrti_frame_unos.columnconfigure(3, weight=3)
        self.cetvrti_frame_unos.columnconfigure(4, weight=3)
        self.cetvrti_frame_unos.columnconfigure(5, weight=3)
        self.cetvrti_frame_unos.rowconfigure(0, weight=1)

        self.saldo_duguje_text = Label(self.cetvrti_frame_unos, text="Saldo duguje:")
        self.saldo_duguje_text.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.saldo_unos_duguje = Label(self.cetvrti_frame_unos, bg="white", font="12", justify="right", text='',
                                       borderwidth=2, relief="groove", width=40)
        self.saldo_unos_duguje.grid(row=0, column=1, padx=10, pady=10, ipadx=5, ipady=5, sticky='w')

        self.saldo_potrazuje_text = Label(self.cetvrti_frame_unos, text="Saldo potrazuje:")
        self.saldo_potrazuje_text.grid(row=0, column=2, padx=10, pady=10, sticky='e')

        self.saldo_unos_potrazuje = Label(self.cetvrti_frame_unos, bg="white", font="12", justify="right", text='',
                                          borderwidth=2, relief="groove", width=40)
        self.saldo_unos_potrazuje.grid(row=0, column=3, padx=10, pady=10, ipadx=5, ipady=5, sticky='w')
        self.ukupan_saldo_text = Label(self.cetvrti_frame_unos, text="Saldo:")
        self.ukupan_saldo_text.grid(row=0, column=4, padx=10, pady=10, sticky='e')
        self.ukupan_saldo = Label(self.cetvrti_frame_unos, bg="white", font="12", justify="right", text='',
                                          borderwidth=2, relief="groove", width=40)
        self.ukupan_saldo.grid(row=0, column=5, padx=10, pady=10, ipadx=5, ipady=5, sticky='w')

        ######################################################################################################
        # Peti label frame za komande knjizenja i stampanja
        self.peti_frame_unos = LabelFrame(self.prozor_unos_naloga, text="Komande", bg="lightblue")
        self.peti_frame_unos.grid(row=4, column=0, padx=10, pady=10, sticky='nsew')
        self.peti_frame_unos.rowconfigure(0, weight=1)
        self.peti_frame_unos.columnconfigure(0, weight=1)
        self.peti_frame_unos.columnconfigure(1, weight=1)
        self.peti_frame_unos.columnconfigure(2, weight=1)
        self.peti_frame_unos.columnconfigure(3, weight=1)
        self.peti_frame_unos.columnconfigure(4, weight=1)
        self.peti_frame_unos.columnconfigure(5, weight=1)

        self.peti_frame_unos.rowconfigure(0, weight=1)
        # Ako je nalog proknjizen dugme za proknjizavanje postaje neaktivno, nema potrebe da se vise puta knjizi nalog
        if da_ne_proknjizen_nalog == "da":
            self.dugme_proknjizi = Button(self.peti_frame_unos, text="Proknjiži nalog", state="disabled",
                                          command=self.proknjizi_nalog)
        else:
            self.dugme_proknjizi = Button(self.peti_frame_unos, text="Proknjiži nalog", bg="#265073", fg="white", command=self.proknjizi_nalog)
        self.dugme_proknjizi.grid(row=0, column=2, padx=10, pady=10, sticky='ew')
        # Ako nalog nije proknjizen ne moze se stampati
        if da_ne_proknjizen_nalog == "da":
            self.dugme_stampa = Button(self.peti_frame_unos, text="Štampaj nalog", bg='#40A2D8', fg='white', command=self.stampaj_nalog)
        else:
            self.dugme_stampa = Button(self.peti_frame_unos, text="Štampaj nalog", state="disabled",
                                       command=self.stampaj_nalog)
        self.dugme_stampa.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        self.tree_tabela_nalog.bind("<ButtonRelease-1>", self.selektuj_red)

        # Citanje stavki naloga iz baze i prikaz u tabeli, racunanje salda
        conn = StavkaNalogaController()
        rezultat_stavke = conn.find_join(id_naloga)
        self.prikaz_podataka_u_tabeli(rezultat_stavke)

    def prikazi_naloge(self, godina):
        self.nalozi_frame = LabelFrame(self.master, text="Nalozi")
        self.nalozi_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.nalozi_frame.columnconfigure(0, weight=1)
        self.nalozi_frame.columnconfigure(1, weight=4)
        self.nalozi_frame.rowconfigure(0, weight=1)

        # Definisanja polja za unos novih naloga
        self.unos_naloga = LabelFrame(self.nalozi_frame, text="Unos naloga")
        self.unos_naloga.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.unos_naloga.columnconfigure(0, weight=1)
        self.unos_naloga.columnconfigure(1, weight=1)
        self.unos_naloga.grid_propagate(False)

        # Definisanje elemenata u polju za unos naloga
        # Label Vrsta naloga
        self.label_vrsta_naloga = Label(self.unos_naloga, text="Vrsta naloga:")
        self.label_vrsta_naloga.grid(row=0, column=0, padx=10, pady=(30, 10), sticky="w")

        # Combobox za izbor vrste naloga
        self.izaberi_vrstu_naloga = StringVar()
        self.vrsta_naloga_combo = ttk.Combobox(self.unos_naloga, textvariable=self.izaberi_vrstu_naloga, state="readonly", background="lightblue", postcommand=self.ucitane_vrste_naloga)
        self.vrsta_naloga_combo.grid(row=0, column=1, padx=10, pady=(30, 10), sticky="ew")

        # Label Broj naloga
        self.label_broj_naloga = Label(self.unos_naloga, text="Broj naloga:")
        self.label_broj_naloga.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        # Input polje za unos broja naloga
        self.broj_novog_naloga = StringVar()
        self.broj_naloga = Entry(self.unos_naloga, textvariable=self.broj_novog_naloga)
        self.broj_naloga.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.broj_naloga.bind("<KeyRelease>", self.__proveri_jezik_broj_naloga)

        # Label datum naloga
        self.label_datum_naloga = Label(self.unos_naloga, text="Datum naloga:")
        self.label_datum_naloga.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Input polje za unos datuma naloga
        self.datum_novog_naloga = DateEntry(self.unos_naloga, selectmode='day', locale='sr_RS', date_pattern='dd.MM.yyyy', font='5')
        self.datum_novog_naloga.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        # Dugme za kreiranje naloga
        self.kreiraj_nalog_dugme = Button(self.unos_naloga, text="Kreiraj nalog", command=self.kreiraj_nalog, bg="lightblue")
        self.kreiraj_nalog_dugme.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Definisanje polja za prikaz liste unetih i proknjizenih naloga
        self.pregled_naloga = LabelFrame(self.nalozi_frame, text="Pregled naloga")
        self.pregled_naloga.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.pregled_naloga.columnconfigure(0, weight=1)
        self.pregled_naloga.rowconfigure(0, weight=1)
        self.pregled_naloga.grid_propagate(False)

        # Definisanje Canvasa zbog stavljanja Scroll bara - ne moze scroll bar u labelframe vec samo u canvas
        self.canvas_pregled_naloga = Canvas(self.pregled_naloga)
        self.canvas_pregled_naloga.grid(row=0, column=0, sticky='nsew')
        self.canvas_pregled_naloga.columnconfigure(0, weight=1)
        self.canvas_pregled_naloga.rowconfigure(0, weight=1)
        # Definisanje tabele sa proknjizenim nalozima
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Treeview", background="#d3d3d3", foreground="black", rowheight=25,
                             fieldbackground="d3d3d3", font=(None, 10))
        # Boja selektrovanog reda
        self.style.map('Treeview', background=[('selected', '#347083')])

        self.my_tree = ttk.Treeview(self.canvas_pregled_naloga)
        self.my_tree.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.my_tree['columns'] = ("R.broj", "Vrsta naloga", "Broj", "Datum", "Proknjižen")
        self.my_tree.column("#0", width=0, stretch=False)
        self.my_tree.column("R.broj", anchor=tk.CENTER, width=40)
        self.my_tree.column("Vrsta naloga", anchor=tk.CENTER, minwidth=150)
        self.my_tree.column("Broj", anchor=tk.CENTER, minwidth=100)
        self.my_tree.column("Datum", anchor=tk.CENTER, minwidth=150)
        self.my_tree.column("Proknjižen", anchor=tk.CENTER, width=50)

        self.treeScroll = ttk.Scrollbar(self.canvas_pregled_naloga)
        self.treeScroll.grid(row=0, column=1, sticky='ns')
        self.treeScroll.configure(command=self.my_tree.yview)
        self.my_tree.configure(yscrollcommand=self.treeScroll.set)

        self.my_tree.heading("#0", anchor=tk.W, text="")
        self.my_tree.heading("R.broj", anchor=tk.CENTER, text="R.broj")
        self.my_tree.heading("Vrsta naloga", anchor=tk.CENTER, text="Vrsta naloga")
        self.my_tree.heading("Broj", anchor=tk.CENTER, text="Broj")
        self.my_tree.heading("Datum", anchor=tk.CENTER, text="Datum")
        self.my_tree.heading("Proknjižen", anchor=tk.CENTER, text="Proknjižen")

        # Prikaz svih naloga iz aktivne godine
        self.svi_nalozi(godina)

        self.buttons_frame = Frame(self.pregled_naloga)
        self.buttons_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.dugme_pregledaj = Button(self.buttons_frame, text="Pregledaj nalog", command=self.pregledaj_nalog, bg="lightblue")
        self.dugme_pregledaj.grid(row=0, column=0, padx=(1, 1), pady=10)
        self.dugme_obrisi = Button(self.buttons_frame, text="   Obriši nalog   ", command=self.poruka_brisanje, bg="#FF6868", fg="white")
        self.dugme_obrisi.grid(row=0, column=1, pady=10)
        self.dugme_formiraj_oris = Button(self.buttons_frame, text="Formiraj ORIS fajl", bg="#FFCF81", fg="black")
        self.dugme_formiraj_oris.grid(row=0, column=2, pady=10)
