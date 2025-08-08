from tkinter import Button, Toplevel, Label, Entry, ttk, messagebox, StringVar, LabelFrame
from racunovodstvo_mvc.controllers.GodinaController import GodinaConnection
from racunovodstvo_mvc.views.godinaframe import GodinaFrame
from racunovodstvo_mvc.controllers.NaloziController import NaloziController
from racunovodstvo_mvc.controllers.KontoController import KontoController
from racunovodstvo_mvc.controllers.StavkaNalogaController import StavkaNalogaController
from racunovodstvo_mvc.views.nalozi import Nalozi
from racunovodstvo_mvc.controllers.BekapController import BekapController
from racunovodstvo_mvc.controllers.KorisnikController import KorisnikController
from mysql.connector import Error
from datetime import datetime
import subprocess
import zipfile
import webbrowser
import os


class Sistem:
    # ********************************** PROZOR SISTEM ************************************** #
    def ucitavanje_godina_combo(self):
        konekcija = GodinaConnection()
        rezultat = konekcija.read()
        sve_godine = []
        for i in rezultat:
            sve_godine.append(i[1])
        self.entry_prebacivanje_pocetnog['values'] = sve_godine

    def unos_godine(self):
        nova_godina = self.entry_otvaranje_godine.get()
        if len(nova_godina) == 0:
            messagebox.showinfo("Upozorenje", "Niste uneli godinu!", parent=self.prozor_sistem)
        elif nova_godina.isdigit():
            try:
                godine = GodinaConnection()
                rezultat = godine.check_godina(nova_godina)
                if rezultat[0][0] == 1:
                    messagebox.showinfo("Greška", "Ova godina je već uneta u bazu podataka!", parent=self.prozor_sistem)
                else:
                    try:
                        godine.insert_godina(nova_godina)
                        promena_godine = GodinaFrame(self.master)
                        promena_godine.prikazi_frame_godina()
                        promena_godine.promena_otvaranje_nove_godine()
                        self.ucitavanje_godina_combo()
                        messagebox.showinfo("Uspešno", "Uspešno ste uneli novu godinu!", parent=self.prozor_sistem)
                    except ValueError:
                        messagebox.showinfo("Hmmmmm", "Nešto nije u redu sa upisom nove godine u bazu!", parent=self.prozor_sistem)
            except ValueError:
                messagebox.showinfo("Hmmmmm", "Nešto nije u redu sa upisom nove godine u bazu!", parent=self.prozor_sistem)

        else:
            messagebox.showinfo("Upozorenje", "Morate uneti samo cifre, bez slova i znakova interpunkcije!", parent=self.prozor_sistem)

    def prebacivanje_pocetnog(self):
        godina = self.entry_prebacivanje_pocetnog.get()
        nalozi = NaloziController()
        rezultat = nalozi.provera_postoji_pocetno_u_godini(godina)
        if rezultat:
            messagebox.showinfo("Upozorenje", "U "+godina+". godini postoji proknjiženo početno stanje!", parent=self.prozor_sistem)
        else:
            pocetna_godina = int(godina)-1
            pocetni_datum = "01.01." + str(pocetna_godina)
            pocetni_datum_obj = datetime.strptime(pocetni_datum, '%d.%m.%Y').date()
            zavrsni_datum = "31.12." + str(pocetna_godina)
            zavrsni_datum_obj = datetime.strptime(zavrsni_datum, '%d.%m.%Y').date()

            konto_conn = KontoController()
            stanja_konta_subanalitika = konto_conn.stanje_kategorije_subanalitika(pocetni_datum_obj, zavrsni_datum_obj)
            novo_pocetno = []

            for stanje in stanja_konta_subanalitika:
                slog = ()
                if stanje[3] > 0:
                    slog = slog+(stanje[0], stanje[3], 'd')
                elif stanje[3] < 0:
                    slog = slog+(stanje[0], abs(stanje[3]), 'p')

                novo_pocetno.append(slog)

            # izbacivanje praznih elemenata iz niza, jer kada je stanje[3] = 0 onda slog() upisuje prazan element u novo_pocetno
            novo_pocetno_stanje = [t for i, t in enumerate(novo_pocetno) if t]
            # Pronjiziti nalog
            vrsta = 'Početno stanje'
            datum_pocetnog_string = "01.01."+godina
            datum_pocetnog = datetime.strptime(datum_pocetnog_string, '%d.%m.%Y').date()
            broj_pocetnog_stanja = "PS-"+godina
            '''
            otvaranje_pocetnog_stanja mora da se stavi da bi se razlikovao unos naloga u bazu kada se kreira obican
            nalog od kreiranja pocetnog stanja za godinu. Kada se kreira obican nalog brisu se polja broj naloga i 
            vrsta, a to bi uzrokovalo gresku jer ta polja se ne koriste kada se kreira pocetno stanje
            '''
            otvaranje_pocetnog_stanja = 'da'
            try:
                nalozi_conn = Nalozi(self.master)
                nalozi_conn.unos_naloga_u_bazu(datum_pocetnog, broj_pocetnog_stanja, vrsta, otvaranje_pocetnog_stanja)
            except ValueError:
                messagebox.showinfo("Hmmmmm", "Nešto nije u redu sa unosom početnog stanja!", parent=self.prozor_sistem)
            else:
                nalozi_conn.prikazi_naloge(godina)
                # pronaci ID naloga
                trazenje_naloga = NaloziController()
                id_naloga = trazenje_naloga.pronadji_poslednji()
                # Proknjiziti stavke naloga sa id naloga
                nalog_pocetni_knjizenje = id_naloga[0][0]
                # Unos nove stavke u bazu
                conn_unos = StavkaNalogaController()

                for stavke_pocetnog_stanja in novo_pocetno_stanje:
                    id_konta = konto_conn.find(stavke_pocetnog_stanja[0])
                    conn_unos.insert_stavka(id_konta[0][0], '', nalog_pocetni_knjizenje, float(stavke_pocetnog_stanja[1]), stavke_pocetnog_stanja[2], '')

    def cuvanje_podataka(self):
        username = 'root'
        password = 'UrLe19023009'
        database = 'racunovodstvo'
        now = datetime.now()
        danasnji_datum = now.strftime("%m%d%Y%H%M%S")
        # naziv_snimljene_baze = "C:\\Users\\PC\\Desktop\\backup"+danasnji_datum+".sql"
        dump_file = 'baza_podataka.sql'
        # naziv_snimljene_baze = ".\\backup\\sacuvano_" + danasnji_datum + ".sql"
        naziv_snimljene_baze = ".\\sacuvano\\sacuvano_finansije" + danasnji_datum + ".zip"
        try:
            subprocess.run(
                ["C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe", "-u", username, "-p%s" % password,
                 database, '--result-file=' + dump_file])

            # Kreiranje ZIP fajla i dodavanje dump fajla i fajlova iz foldera
            zip_file = naziv_snimljene_baze
            folder_path = os.getcwd() + "\\efakture"

            with zipfile.ZipFile(zip_file, 'w') as zipf:
                # Dodavanje dump fajla u ZIP arhivu
                zipf.write(dump_file)
                os.remove(dump_file)  # Brisanje privremenog dump fajla

                # Dodavanje fajlova iz foldera u ZIP arhivu
                for foldername, subfolders, filenames in os.walk(folder_path):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))

            datum_bekapa = now.strftime('%Y-%m-%d %H:%M:%S')
            bekap = BekapController()
            bekap.insert_bekap(datum_bekapa)
            messagebox.showinfo("Odlično", "Uspešno su sačuvani podaci!", parent=self.prozor_sistem)
            path = ".\\sacuvano\\"
            webbrowser.open(os.path.realpath(path))
        except ValueError:
            messagebox.showinfo("Hmmmmm", "Nešto nije u redu sa bekapom!", parent=self.prozor_sistem)

        '''
        try:
            with open(naziv_snimljene_baze, 'w') as output:
                c = subprocess.Popen(["C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe", "-u", username, "-p%s" % password, database],
                                 stdout=output, shell=True)

            datum_bekapa = now.strftime('%Y-%m-%d %H:%M:%S')
            bekap = BekapController()
            bekap.insert_bekap(datum_bekapa)
            messagebox.showinfo("Odlično", "Uspešno su sačuvani podaci!", parent=self.prozor_sistem)
        except ValueError:
            messagebox.showinfo("Hmmmmm", "Nešto nije u redu sa bekapom!", parent=self.prozor_sistem)
        '''

    def poslednji_bekap(self):
        try:
            bekap=BekapController()
            rezultat = bekap.find_last()
            if len(rezultat) == 0:
                self.datum_poslednjeg_bekapa.set('Još uvek nije radjen bekap podataka')
            else:
                vreme_poslednjeg_bekapa=rezultat[0][1].strftime("%d.%m.%Y, %H:%M:%S")
                self.datum_poslednjeg_bekapa.set(vreme_poslednjeg_bekapa)
        except ValueError:
            messagebox.showinfo("Hmmmmm", "Nešto nije u redu sa bazom podataka!", parent=self.prozor_sistem)

    def pronadji_podatke_o_organizaciji(self):
        organizacija_kontroler = KorisnikController()
        rezultat = organizacija_kontroler.find(1)
        # OVDE CU MORATI DA PROVERIM AKO IMA ORGANIZACIJA, DA NEKA POLJA KOJA NISU U BAZI, U PROGRAMU BUDU " "
        if rezultat:
            self.dugme_dodaj_organizaciju.config(state="disabled")
            if rezultat[0][2]:
                self.naziv_organizacije_entry.insert(0, rezultat[0][2])
            if rezultat[0][3]:
                self.jbkjs_entry.insert(0, rezultat[0][3])
            if rezultat[0][4]:
                self.program_entry.insert(0, rezultat[0][4])
            if rezultat[0][5]:
                self.projekat_entry.insert(0, rezultat[0][5])
            if rezultat[0][6]:
                self.funkcionalna_entry.insert(0, rezultat[0][6])
            if rezultat[0][7]:
                self.valuta_entry.insert(0, rezultat[0][7])
            if rezultat[0][1]:
                self.racunovodja_entry.insert(0, rezultat[0][1])

    def ocitaj_podatke(self):
        naziv = self.naziv_organizacije_entry.get()
        jbjks = self.jbkjs_entry.get()
        program = self.program_entry.get()
        projekat = self.projekat_entry.get()
        funkcionalna = self.funkcionalna_entry.get()
        valuta = self.valuta_entry.get()
        racunovodja = self.racunovodja_entry.get()

        return racunovodja, naziv, jbjks, program, projekat, funkcionalna, valuta

    def dodaj_organizaciju(self):
        ocitani_podaci = self.ocitaj_podatke()
        try:
            organizacija_kontroler = KorisnikController()
            organizacija_kontroler.unesi_podatke(ocitani_podaci[0], ocitani_podaci[1], ocitani_podaci[2], ocitani_podaci[3], ocitani_podaci[4], ocitani_podaci[5], ocitani_podaci[6])
            # ponovo učitati prozor sa podacima
            self.prozor_podaci_organizacija.destroy()
            self.organizacija_prozor()
            messagebox.showinfo("Uspesno", "Uspešno su uneti podaci!", parent=self.prozor_podaci_organizacija)
        except Error as e:
            messagebox.showwarning("Greška", "Nešto nije u redu sa unosom podataka!", parent=self.prozor_podaci_organizacija)

    def update_organizaciju(self):
        ocitani_podaci = self.ocitaj_podatke()
        try:
            organizacija_kontroler = KorisnikController()
            organizacija_kontroler.izmeni_podatke(ocitani_podaci[0], ocitani_podaci[1], ocitani_podaci[2], ocitani_podaci[3], ocitani_podaci[4], ocitani_podaci[5], ocitani_podaci[6])
            # ponovo učitati prozor sa podacima
            self.prozor_podaci_organizacija.destroy()
            self.organizacija_prozor()
            messagebox.showinfo("Uspesno", "Uspešno su izmenjeni podaci!", parent=self.prozor_podaci_organizacija)
        except Error as e:
            messagebox.showwarning("Greška", "Nešto nije u redu sa izmenom podataka!", parent=self.prozor_podaci_organizacija)

    def organizacija_prozor(self):
        self.prozor_podaci_organizacija = Toplevel(self.prozor_sistem)
        self.prozor_podaci_organizacija.grab_set()
        self.prozor_podaci_organizacija.title("Podaci o organizaciji")
        self.prozor_podaci_organizacija.geometry("500x500")
        self.prozor_podaci_organizacija.resizable(False, False)
        self.prozor_podaci_organizacija.columnconfigure(0, weight=1)
        self.prozor_podaci_organizacija.rowconfigure(0, weight=4)
        self.prozor_podaci_organizacija.rowconfigure(1, weight=1)

        # Prvi frame za entry polje naziv
        self.entry_polja_organizacija = LabelFrame(self.prozor_podaci_organizacija, text="Podaci")
        self.entry_polja_organizacija.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.entry_polja_organizacija.columnconfigure(0, weight=1)
        self.entry_polja_organizacija.columnconfigure(1, weight=3)
        self.entry_polja_organizacija.rowconfigure(0, weight=1)
        self.entry_polja_organizacija.rowconfigure(1, weight=1)
        self.entry_polja_organizacija.rowconfigure(2, weight=1)
        self.entry_polja_organizacija.rowconfigure(3, weight=1)
        self.entry_polja_organizacija.rowconfigure(4, weight=1)
        self.entry_polja_organizacija.rowconfigure(5, weight=1)
        self.entry_polja_organizacija.rowconfigure(6, weight=1)

        # Label i polje za unos naziva organizacije
        self.naziv_organizacije_label = Label(self.entry_polja_organizacija, text="Naziv organizacije:")
        self.naziv_organizacije_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.naziv_organizacije_entry = Entry(self.entry_polja_organizacija)
        self.naziv_organizacije_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        # self.naziv_entry_nalog.bind("<KeyRelease>", self.__proveri_jezik)

        # Label i polje za unos JBKJS
        self.jbkjs_label = Label(self.entry_polja_organizacija, text="JBKJS:")
        self.jbkjs_label.grid(row=1, column=0, padx=10, sticky='w')
        self.jbkjs_entry = Entry(self.entry_polja_organizacija)
        self.jbkjs_entry.grid(row=1, column=1, padx=10, sticky='ew')

        # Label i polje za sifre programa
        self.program_label = Label(self.entry_polja_organizacija, text="Šifra programa:")
        self.program_label.grid(row=2, column=0, padx=10, sticky='w')
        self.program_entry = Entry(self.entry_polja_organizacija)
        self.program_entry.grid(row=2, column=1, padx=10, sticky='ew')

        # Label i polje za sifre projekta
        self.projekat_label = Label(self.entry_polja_organizacija, text="Šifra projekta:")
        self.projekat_label.grid(row=3, column=0, padx=10, sticky='w')
        self.projekat_entry = Entry(self.entry_polja_organizacija)
        self.projekat_entry.grid(row=3, column=1, padx=10, sticky='ew')

        # Label i polje za sifre funkcionalne klasifikacije
        self.funkcionalna_label = Label(self.entry_polja_organizacija, text="Funkcionalna klasifikacija:")
        self.funkcionalna_label.grid(row=4, column=0, padx=10, sticky='w')
        self.funkcionalna_entry = Entry(self.entry_polja_organizacija)
        self.funkcionalna_entry.grid(row=4, column=1, padx=10, sticky='ew')

        # Label i polje za sifre valute
        self.valuta_label = Label(self.entry_polja_organizacija, text="Šifra valute:")
        self.valuta_label.grid(row=5, column=0, padx=10, sticky='w')
        self.valuta_entry = Entry(self.entry_polja_organizacija)
        self.valuta_entry.grid(row=5, column=1, padx=10, sticky='ew')

        # Label i polje za ime i prezime knjigovodje
        self.racunovodja_label = Label(self.entry_polja_organizacija, text="Računovodja (ime i prezime):")
        self.racunovodja_label.grid(row=6, column=0, padx=10, sticky='w')
        self.racunovodja_entry = Entry(self.entry_polja_organizacija)
        self.racunovodja_entry.grid(row=6, column=1, padx=10, sticky='ew')

        # Drugi frame za dugmad Dodaj, Izmeni, Obrisi i Izaberi
        self.polje_dugmad_organizacija = LabelFrame(self.prozor_podaci_organizacija, text="Komande", bg="lightblue")
        self.polje_dugmad_organizacija.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.polje_dugmad_organizacija.rowconfigure(0, weight=1)
        self.polje_dugmad_organizacija.columnconfigure(0, weight=1)
        self.polje_dugmad_organizacija.columnconfigure(1, weight=1)
        self.polje_dugmad_organizacija.columnconfigure(2, weight=1)
        self.polje_dugmad_organizacija.columnconfigure(3, weight=1)

        self.dugme_dodaj_organizaciju = Button(self.polje_dugmad_organizacija, text="Dodaj organizaciju", bg='#40A2D8', fg='white', command=self.dodaj_organizaciju)
        self.dugme_dodaj_organizaciju.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        # self.dugme_dodaj_nalog.bind("<Return>", self.__proveri_jezik, add='+')
        # self.dugme_dodaj_nalog.bind("<ButtonRelease>", self.__proveri_jezik, add='+')

        self.dugme_izmeni_organizaciju = Button(self.polje_dugmad_organizacija, text="Izmeni organizaciju", bg="#265073", fg="white", command=self.update_organizaciju)
        self.dugme_izmeni_organizaciju.grid(row=0, column=2, padx=10, pady=10, sticky='ew')
        # self.dugme_izmeni_nalog.bind("<Return>", self.__proveri_jezik, add='+')
        # self.dugme_izmeni_nalog.bind("<ButtonRelease-1>", self.__proveri_jezik, add='+')
        self.pronadji_podatke_o_organizaciji()

    def __init__(self, master):
        self.master = master
        self.prozor_sistem = Toplevel()
        self.prozor_sistem.grab_set()
        self.prozor_sistem.title("Podešavanje sistema")
        self.prozor_sistem.geometry("800x150")
        self.prozor_sistem.resizable(False, False)
        self.prozor_sistem.columnconfigure(0, weight=1)
        self.prozor_sistem.rowconfigure(0, weight=1)

        self.prozor_podaci_organizacija = None
        self.entry_polja_organizacija = None
        self.naziv_organizacije_label = None
        self.naziv_organizacije_entry = None
        self.jbkjs_label = None
        self.jbkjs_entry = None
        self.program_label = None
        self.program_entry = None
        self.projekat_entry = None
        self.projekat_label = None
        self.funkcionalna_entry = None
        self.funkcionalna_label = None
        self.valuta_entry = None
        self.valuta_label = None
        self.racunovodja_entry = None
        self.racunovodja_label = None
        self.polje_dugmad_organizacija = None
        self.dugme_dodaj_organizaciju = None
        self.dugme_izmeni_organizaciju = None

        self.notebook = ttk.Notebook(self.prozor_sistem)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.tab_otvaranje_godine = ttk.Frame(self.notebook)
        self.tab_prebacivanje_pocetnog_stanja = ttk.Frame(self.notebook)
        self.tab_unos_korisnika = ttk.Frame(self.notebook)
        self.tab_backup_podataka = ttk.Frame(self.notebook)
        self.tab_organizacija = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_otvaranje_godine, text='Otvaranje nove godine')
        self.notebook.add(self.tab_prebacivanje_pocetnog_stanja, text='Prebacivanje početnog stanja')
        self.notebook.add(self.tab_backup_podataka, text='Backup podataka')
        self.notebook.add(self.tab_organizacija, text='Organizacija')
        # ************************************ Tab 1 Otvaranje godine ************************************** #
        self.label_otvaranje_godine = Label(self.tab_otvaranje_godine, text="Unesi novu godinu:")
        self.label_otvaranje_godine.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.entry_otvaranje_godine = Entry(self.tab_otvaranje_godine)
        self.entry_otvaranje_godine.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.button_otvaranje_godine = Button(self.tab_otvaranje_godine, text="Potvrdi unos godine", command=self.unos_godine)
        self.button_otvaranje_godine.grid(row=0, column=2, padx=10, pady=10, sticky='w')

        # ************************************ Tab 2 Prebacivanje pocetnog stanja ************************** #
        self.label_prebacivanje_pocetnog = Label(self.tab_prebacivanje_pocetnog_stanja, text="Unesite godinu u koju prebacujete početno stanje:")
        self.label_prebacivanje_pocetnog.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.entry_prebacivanje_pocetnog = ttk.Combobox(self.tab_prebacivanje_pocetnog_stanja)
        self.entry_prebacivanje_pocetnog.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        self.ucitavanje_godina_combo()
        self.button_prebacivanje_pocetnog = Button(self.tab_prebacivanje_pocetnog_stanja, text="Potvrdi prenos početnog stanja", command=self.prebacivanje_pocetnog)
        self.button_prebacivanje_pocetnog.grid(row=0, column=2, padx=10, pady=10, sticky='w')

        # ************************************* Tab 3 Unos novog korisnika ********************************* #
        self.button_backup = Button(self.tab_backup_podataka, text="Sačuvaj podatke", command=self.cuvanje_podataka)
        self.button_backup.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.datum_poslednjeg_bekapa = StringVar()
        self.poslednji_bekap()
        self.obavestenje = Label(self.tab_backup_podataka, text="Datum poslednjeg backup-a:  " + self.datum_poslednjeg_bekapa.get())
        self.obavestenje.grid(row=0, column=2, padx=10, pady=10)

        # ************************************* Tab 4 Podaci o organizaciji ********************************* #
        self.button_organizacija_podaci = Button(self.tab_organizacija, text="Podaci o organizaciji", command=self.organizacija_prozor)
        self.button_organizacija_podaci.grid(row=0, column=1, padx=10, pady=10, sticky='w')
