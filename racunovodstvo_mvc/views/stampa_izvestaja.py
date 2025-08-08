from fpdf import FPDF
from racunovodstvo_mvc.controllers.AplikacijaController import AplikacijaController
from racunovodstvo_mvc.controllers.KorisnikController import KorisnikController
from datetime import date
import webbrowser
import locale
import xlsxwriter
import os

class STAMPA(FPDF):

    def __init__(self, orient, mera, form):
        FPDF.__init__(self, orientation=orient, unit=mera, format=form)
        self.set_font('Helvetica', '', 9)
        # self.fontsize=fontsize

class PDF(FPDF):

    def __init__(self, orient, mera, form):
        FPDF.__init__(self, orientation=orient, unit=mera, format=form)
        self.set_font('Helvetica', '', 9)
        # self.fontsize=fontsize

    def header(self):
        # Logo
        # x=110.9, y=16.1
        # self.image(name='logo.png', x=110.6, y=15.9, w=72.9)
        '''
        firma = FirmaModel()
        podaci_firma = firma.read()
        stampa = StampaIzvestaja()
        naziv_firme = stampa.zamena_slova(podaci_firma[0][1])
        mesto_firme = stampa.zamena_slova(podaci_firma[0][2])
        '''
        # Prvo se u tabeli aplikacija trazi sifra korisnika koju sam uneo na pocetnom ekranu u delu podesavanja
        conn_aplikacija = AplikacijaController()
        pronadjena_aplikacija = conn_aplikacija.find()
        id_korisnika = pronadjena_aplikacija[0][1]
        # Pomocu sifre korisnika u tabeli aplikacija trazim naziv firme i (ime i prezime korisnika)
        conn_korisnik = KorisnikController()
        pronadjen_korisnik = conn_korisnik.find(id_korisnika)
        stampa = StampaIzvestaja()
        # Naziv firme
        naziv = pronadjen_korisnik[0][2]
        firma = stampa.zamena_slova(naziv)
        # Ime i prezime korisnika
        # ime = pronadjen_korisnik[0][1]
        # kontirao = self.zamena_slova(ime)
        # Arial bold 15
        self.set_font('Helvetica', '', 12)
        # textcolor
        self.set_text_color(r=65, g=105, b=225)
        if self.page_no() == 1:
            # Title
            self.text(self.l_margin, 1+1, txt=firma)
            if self.cur_orientation == "L":
                self.line(1, 2.5, 28, 2.5)
            else:
                self.line(1, 2.5, 20, 2.5)
            self.cell(20, 2, "", 0, 1)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Helvetica', 'I', 9)
        # Page number
        self.cell(0, 27, 'Strana ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')


class StampaIzvestaja:

    def zamena_slova(self, rec):
        if rec is not None:
            return rec.replace('č', 'c').replace('ž', 'z').replace('ć', 'c').replace('š', 's').replace('Č', 'C').replace('Ž', 'Z').replace('Ć', 'C').replace('Š', 'S').replace('đ', 'dj').replace('Đ', 'Dj')
        else:
            return ""

    def broj_karaktera(self, tekst, duzina):
        return tekst[:duzina]

    def stampa_naloga(self, rezultat_stavke, datum_naloga, broj_naloga, datum_knjizenja):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        pdf = PDF('portrait', 'cm', 'A4')
        # pdf.accept_page_break()
        pdf.add_page()
        duguje = 0
        potrazuje = 0

        for record in rezultat_stavke:

            # Racunanje salda naloga duguje/potrazuje

            if record[5] == 'd':
                duguje += record[4]
            else:
                potrazuje += record[4]

        duguje_prikaz = locale.format_string('%10.2f', duguje, grouping=True)
        potrazuje_prikaz = locale.format_string('%10.2f', potrazuje, grouping=True)

        saldo = duguje - potrazuje
        saldo_ukupno = saldo
        saldo_ukupno_formatiran = locale.format_string('%10.2f', saldo_ukupno, grouping=True)

        pdf.set_font('Helvetica', '', 11)
        pdf.cell(16, 1, 'Datum knjizenja:', 0, 0, 'R')
        pdf.cell(3, 1, datum_knjizenja + ".", 0, 1, 'L')
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(19, 1, 'Nalog za knjizenje: ' + broj_naloga + '  ' + datum_naloga, 0, 1, 'C')
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(2, 0.7, 'Duguje:', 0, 0, 'L')
        pdf.cell(6, 0.7, duguje_prikaz, 0, 1, 'R')
        pdf.cell(2, 0.7, 'Potrazuje:', 0, 0, 'L')
        pdf.cell(6, 0.7, potrazuje_prikaz, 0, 1, 'R')
        pdf.cell(2, 0.7, 'Saldo:', 0, 0, 'L')
        pdf.cell(6, 0.7, saldo_ukupno_formatiran, 0, 1, 'R')
        # pdf.line(1, 7, 20, 7)
        pdf.set_fill_color(221, 221, 221)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(4, 1, 'Konto', 0, 0, 'L', fill=True)
        pdf.cell(6, 1, 'Opis konta', 0, 0, 'L', fill=True)
        pdf.cell(3, 1, 'Duguje', 0, 0, 'R', fill=True)
        pdf.cell(3, 1, 'Potrazuje', 0, 0, 'R', fill=True)
        pdf.cell(3, 1, 'Izvor fin.', 0, 1, 'C', fill=True)
        # pdf.line(1, 8, 20, 8)
        pdf.set_font('Helvetica', '', 11)

        for red in rezultat_stavke:
            konto_o = self.zamena_slova(red[1])
            konto_n = self.zamena_slova(red[2])
            konto_oznaka = self.broj_karaktera(konto_o, 15)
            konto_naziv = self.broj_karaktera(konto_n, 28)
            iznos = locale.format_string('%10.2f', red[4], grouping=True)
            pdf.cell(4, 0.7, konto_oznaka, 0, 0, 'L')
            pdf.cell(6, 0.7, konto_naziv, 0, 0, 'L')
            if red[5] == 'd':
                pdf.cell(3, 0.7, iznos, 0, 0, 'R')
                pdf.cell(3, 0.7, '', 0, 0, 'R')
                pdf.cell(3, 0.7, red[3], 0, 1, 'C')
            else:
                pdf.cell(3, 0.7, '', 0, 0, 'R')
                pdf.cell(3, 0.7, iznos, 0, 0, 'R')
                pdf.cell(3, 0.7, red[3], 0, 1, 'C')

        # Ukupno za nalog

        pdf.set_fill_color(221, 221, 221)
        pdf.set_font('Helvetica', 'B', 12)
        # pdf.set_font('Arial', 'B', 12)
        pdf.cell(4, 1, 'Ukupno:', 0, 0, 'L', fill=True)
        pdf.cell(6, 1, '', 0, 0, 'L', fill=True)
        pdf.cell(3, 1, duguje_prikaz, 0, 0, 'R', fill=True)
        pdf.cell(3, 1, potrazuje_prikaz, 0, 0, 'R', fill=True)
        pdf.cell(3, 1, '', 0, 1, 'C', fill=True)

        pdf.ln(2)
        pdf.cell(5, 1, 'Kontirao:', 0, 1, 'C')
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(6, 1, "______________________", 0, 1, 'L')

        # pdf.cell(5, 1, kontirao, 0, 1, 'C')
        pdf.output('nalog.pdf', 'F')

        webbrowser.open_new(r'nalog.pdf')

    def stampa_kartice_konta(self, rezultat_stavke, oznaka_konta_izvestaj):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        pdf = PDF('portrait', 'cm', 'A4')
        # pdf.accept_page_break()
        pdf.add_page()
        duguje = 0
        potrazuje = 0

        for record in rezultat_stavke:

            # Racunanje salda naloga duguje/potrazuje

            if record[4] == 'd':
                duguje += record[3]
            else:
                potrazuje += record[3]

        duguje_prikaz = locale.format_string('%10.2f', duguje, grouping=True)
        potrazuje_prikaz = locale.format_string('%10.2f', potrazuje, grouping=True)

        saldo = duguje - potrazuje
        saldo_ukupno = saldo
        saldo_ukupno_formatiran = locale.format_string('%10.2f', saldo_ukupno, grouping=True)
        oznaka_konta_za_stampu = self.zamena_slova(oznaka_konta_izvestaj)
        today = date.today()
        danasnji_datum = today.strftime("%d.%m.%Y")
        pdf.set_font('Helvetica', '', 11)
        # pdf.cell(13, 1, firma, 0, 0, 'L')
        pdf.cell(16, 1, 'Datum stampe:', 0, 0, 'R')
        pdf.cell(3, 1, danasnji_datum + ".", 0, 1, 'L')
        # pdf.cell(19, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(19, 1, 'Kartica konta: ' + oznaka_konta_za_stampu, 0, 1, 'C')
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(2, 0.7, 'Duguje:', 0, 0, 'L')
        pdf.cell(6, 0.7, duguje_prikaz, 0, 1, 'R')
        pdf.cell(2, 0.7, 'Potrazuje:', 0, 0, 'L')
        pdf.cell(6, 0.7, potrazuje_prikaz, 0, 1, 'R')
        pdf.cell(2, 0.7, 'Saldo:', 0, 0, 'L')
        pdf.cell(6, 0.7, saldo_ukupno_formatiran, 0, 1, 'R')
        #pdf.line(1, 7, 20, 7)
        pdf.set_fill_color(221, 221, 221)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(4, 1, 'Broj naloga', 0, 0, 'C', fill=True)
        pdf.cell(6, 1, 'Datum naloga', 0, 0, 'C', fill=True)
        pdf.cell(4, 1, 'Duguje', 0, 0, 'R', fill=True)
        pdf.cell(4, 1, 'Potrazuje', 0, 1, 'R', fill=True)
        #pdf.line(1, 8, 20, 8)
        pdf.set_font('Helvetica', '', 10)

        for red in rezultat_stavke:

            pdf.cell(4, 0.5, red[1], 0, 0, 'C')
            pdf.cell(6, 0.5, red[2].strftime("%d.%m.%Y"), 0, 0, 'C')
            if red[4] == 'd':
                pdf.cell(4, 0.5, locale.format_string('%10.2f', red[3], grouping=True), 0, 0, 'R')
                pdf.cell(4, 0.5, '', 0, 1, 'R')

            else:
                pdf.cell(4, 0.5, '', 0, 0, 'R')
                pdf.cell(4, 0.5, locale.format_string('%10.2f', red[3], grouping=True), 0, 1, 'R')

        # Ukupno za nalog
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(4, 1, 'Ukupno:', 0, 0, 'L', fill=True)
        pdf.cell(6, 1, '', 0, 0, 'L', fill=True)
        pdf.cell(4, 1, duguje_prikaz, 0, 0, 'R', fill=True)
        pdf.cell(4, 1, potrazuje_prikaz, 0, 1, 'R', fill=True)
        pdf.ln(2)

        # pdf.cell(5, 1, kontirao, 0, 1, 'C')
        pdf.output('kartica.pdf', 'F')

        webbrowser.open_new(r'kartica.pdf')

    def stampa_kartice_konta_stari(self, rezultat_stavke, oznaka_konta_izvestaj):
        duguje = 0
        potrazuje = 0
        locale.setlocale(locale.LC_ALL, 'de_DE')
        for record in rezultat_stavke:

            # Racunanje salda naloga duguje/potrazuje

            if record[4] == 'd':
                duguje += record[3]
            else:
                potrazuje += record[3]

        duguje_prikaz = locale.format_string('%10.2f', duguje, grouping=True)
        potrazuje_prikaz = locale.format_string('%10.2f', potrazuje, grouping=True)

        saldo = duguje - potrazuje
        saldo_ukupno = saldo
        saldo_ukupno_formatiran = locale.format_string('%10.2f', saldo_ukupno, grouping=True)

        pdf = FPDF('P', 'cm', 'A4')
        #pdf.accept_page_break()
        pdf.add_page()

        # Prvo se u tabeli aplikacija trazi sifra korisnika koju sam uneo na pocetnom ekranu u delu podesavanja
        conn_aplikacija = AplikacijaController()
        pronadjena_aplikacija = conn_aplikacija.find()
        id_korisnika = pronadjena_aplikacija[0][1]
        # Pomocu sifre korisnika u tabeli aplikacija trazim naziv firme i (ime i prezime korisnika)
        conn_korisnik = KorisnikController()
        pronadjen_korisnik = conn_korisnik.find(id_korisnika)
        # Naziv firme
        naziv = pronadjen_korisnik[0][2]

        oznaka_konta_za_stampu = self.zamena_slova(oznaka_konta_izvestaj)
        today = date.today()
        danasnji_datum = today.strftime("%d.%m.%Y")
        pdf.set_font('Helvetica', '', 11)
        # pdf.cell(13, 1, firma, 0, 0, 'L')
        pdf.cell(3, 1, 'Datum stampe:', 0, 0, 'L')
        pdf.cell(3, 1, danasnji_datum, 0, 1, 'R')
        # pdf.cell(19, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(19, 1, 'Kartica konta: '+oznaka_konta_za_stampu, 0, 1, 'C')
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(2, 1, 'Duguje:', 0, 0, 'L')
        pdf.cell(6, 1, duguje_prikaz, 0, 1, 'R')
        pdf.cell(2, 1, 'Potrazuje:', 0, 0, 'L')
        pdf.cell(6, 1, potrazuje_prikaz, 0, 1, 'R')
        pdf.cell(2, 1, 'Saldo:', 0, 0, 'L')
        pdf.cell(6, 1, saldo_ukupno_formatiran, 0, 1, 'R')
        pdf.line(1, 7, 20, 7)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(4, 1, 'Broj naloga', 0, 0, 'C')
        pdf.cell(6, 1, 'Datum naloga', 0, 0, 'C')
        pdf.cell(4, 1, 'Duguje', 0, 0, 'R')
        pdf.cell(4, 1, 'Potrazuje', 0, 1, 'R')
        pdf.line(1, 8, 20, 8)
        pdf.set_font('Arial', '', 10)

        redovi_po_strani = 7

        for red in rezultat_stavke:

            pdf.cell(4, 1, red[1], 0, 0, 'C')
            pdf.cell(6, 1, red[2].strftime("%d.%m.%Y"), 0, 0, 'C')
            if red[4] == 'd':
                pdf.cell(4, 1, locale.format_string('%10.2f', red[3], grouping=True), 0, 0, 'R')
                pdf.cell(4, 1, '', 0, 1, 'R')

            else:
                pdf.cell(4, 1, '', 0, 0, 'R')
                pdf.cell(4, 1, locale.format_string('%10.2f', red[3], grouping=True), 0, 1, 'R')

            if redovi_po_strani > 21:
                pdf.accept_page_break()
                pdf.add_page()
                pdf.cell(19, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
                redovi_po_strani = 0

            redovi_po_strani += 1
            # ukupan_broj_redova += 1

        # Ukupno za nalog
        pdf.line(1, redovi_po_strani + 1, 20, redovi_po_strani + 1)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(4, 1, 'Ukupno:', 0, 0, 'L')
        pdf.cell(6, 1, '', 0, 0, 'L')
        pdf.cell(4, 1, duguje_prikaz, 0, 0, 'R')
        pdf.cell(4, 1, potrazuje_prikaz, 0, 0, 'R')
        pdf.cell(3, 1, '', 0, 1, 'C')
        pdf.line(1, redovi_po_strani + 2, 20, redovi_po_strani + 2)
        pdf.ln(2)

        # pdf.cell(5, 1, kontirao, 0, 1, 'C')
        pdf.output('kartica.pdf', 'F')

        webbrowser.open_new(r'kartica.pdf')

    def stampa_zakljucni_list(self, rezultat, pocetni, krajnji):
        # Ako nema rezultata u okviru trazenog datuma da ne radi nista
        if rezultat is not None:
            locale.setlocale(locale.LC_ALL, 'de_DE')

            pdf = PDF('landscape', 'cm', 'A4')
            pdf.add_page()

            today = date.today()
            danasnji_datum = today.strftime("%d.%m.%Y")
            od_datuma=pocetni.strftime("%d.%m.%Y")
            do_datuma=krajnji.strftime("%d.%m.%Y")
            pdf.set_font('Helvetica', '', 11)
            #pdf.cell(20, 1, firma, 0, 0, 'L')
            pdf.cell(24, 1, 'Datum stampe:', 0, 0, 'R')
            pdf.cell(4, 1, danasnji_datum + ".", 0, 1, 'L')
            #pdf.cell(28, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(28, 1, 'ZAKLJUCNI LIST', 0, 1, 'C')
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(28, 1, 'za period: ' + od_datuma + '. do ' + do_datuma+'.', 0, 1, 'C')
            pdf.set_font('Helvetica', '', 10)
            #pdf.line(1, 5, 28, 5)
            pdf.set_fill_color(221, 221, 221)
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(8, 0.6, '', 0, 0, 'C')
            pdf.cell(5, 0.6, 'Pocetno stanje', 0, 0, 'C')
            pdf.cell(5, 0.6, 'Tekuci promet', 0, 0, 'C')
            pdf.cell(5, 0.6, 'Ukupan promet', 0, 0, 'C')
            pdf.cell(5, 0.6, 'Saldo', 0, 1, 'C')
            pdf.cell(2, 1, 'Konto', 0, 0, 'C')
            pdf.cell(6, 1, 'Naziv konta', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Potrazuje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Potrazuje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Potrazuje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2.5, 1, 'Potrazuje', 0, 1, 'C')
            #pdf.line(1, 8, 25, 8)
            pdf.set_font('Helvetica', '', 8)
            for red in rezultat:
                if red[0][-3:] == '000' or red[0][-4] == '0000' or red[0][-5] == '00000':
                    pdf.set_font('Helvetica', 'B', 7)
                    pdf.cell(2, 1, red[0], 0, 0, 'C', fill=True)
                    pdf.cell(6, 1, self.broj_karaktera(self.zamena_slova(red[1]), 35), 0, 0, 'L', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[2], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[3], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[5], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[6], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[7], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[8], grouping=True), 0, 0, 'R', fill=True)
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[9], grouping=True), 0, 1, 'R', fill=True)
                else:
                    pdf.set_font('Helvetica', '', 7)
                    pdf.cell(2, 1, red[0], 0, 0, 'C')
                    pdf.cell(6, 1, self.broj_karaktera(self.zamena_slova(red[1]), 35), 0, 0, 'L')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[2], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[3], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[5], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[6], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[7], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[8], grouping=True), 0, 0, 'R')
                    pdf.cell(2.5, 1, locale.format_string('%10.2f', red[9], grouping=True), 0, 1, 'R')

            # pdf.cell(5, 1, kontirao, 0, 1, 'C')
            pdf.output('zakljucni.pdf', 'F')

            webbrowser.open_new(r'zakljucni.pdf')

    def stampa_zakljucni_list_stari(self, rezultat, pocetni, krajnji):
        # Ako nema rezultata u okviru trazenog datuma da ne radi nista
        if rezultat is not None:
            locale.setlocale(locale.LC_ALL, 'de_DE')

            pdf = FPDF('L', 'cm', 'A4')
            pdf.accept_page_break()
            pdf.add_page()

            # Prvo se u tabeli aplikacija trazi sifra korisnika koju sam uneo na pocetnom ekranu u delu podesavanja
            conn_aplikacija = AplikacijaController()
            pronadjena_aplikacija = conn_aplikacija.find()
            id_korisnika = pronadjena_aplikacija[0][1]
            # Pomocu sifre korisnika u tabeli aplikacija trazim naziv firme i (ime i prezime korisnika)
            conn_korisnik = KorisnikController()
            pronadjen_korisnik = conn_korisnik.find(id_korisnika)
            # Naziv firme
            naziv = pronadjen_korisnik[0][2]
            firma = self.zamena_slova(naziv)
            # oznaka_konta_za_stampu = self.zamena_slova(oznaka_konta_izvestaj)
            today = date.today()
            danasnji_datum = today.strftime("%d.%m.%Y")
            od_datuma = pocetni.strftime("%d.%m.%Y")
            do_datuma = krajnji.strftime("%d.%m.%Y")
            pdf.set_font('Arial', '', 11)
            pdf.cell(20, 1, firma, 0, 0, 'L')
            pdf.cell(3, 1, 'Datum stampe:', 0, 0, 'L')
            pdf.cell(4, 1, danasnji_datum, 0, 1, 'R')
            pdf.cell(28, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(28, 1, 'ZAKLJUCNI LIST', 0, 1, 'C')
            pdf.set_font('Arial', '', 12)
            pdf.cell(28, 1, 'za period: ' + od_datuma + '. do ' + do_datuma + '.', 0, 1, 'C')
            pdf.set_font('Arial', '', 10)
            pdf.line(1, 5, 28, 5)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(8, 1, '', 0, 0, 'C')
            pdf.cell(4, 1, 'Pocetno stanje', 0, 0, 'C')
            pdf.cell(4, 1, 'Tekuci promet', 0, 0, 'C')
            pdf.cell(4, 1, 'Ukupan promet', 0, 0, 'C')
            pdf.cell(4, 1, 'Saldo', 0, 1, 'C')
            pdf.cell(2, 1, 'Konto', 0, 0, 'C')
            pdf.cell(6, 1, 'Naziv konta', 0, 0, 'C')
            pdf.cell(2, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2, 1, 'Potrazuje', 0, 0, 'C')
            pdf.cell(2, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2, 1, 'Potrazuje', 0, 0, 'C')
            pdf.cell(2, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2, 1, 'Potrazuje', 0, 0, 'C')
            pdf.cell(2, 1, 'Duguje', 0, 0, 'C')
            pdf.cell(2, 1, 'Potrazuje', 0, 1, 'C')
            pdf.line(1, 7, 28, 7)
            pdf.set_font('Arial', '', 8)

            redovi_po_strani = 8

            for red in rezultat:
                if red[0][-3:] == '000' or red[0][-4] == '0000' or red[0][-5] == '00000':
                    pdf.set_font('Arial', 'B', 7)
                    if pdf.page_no() == 1:
                        pdf.line(1, redovi_po_strani, 28, redovi_po_strani)
                    else:
                        pdf.line(1, redovi_po_strani + 2, 28, redovi_po_strani + 2)
                else:
                    pdf.set_font('Arial', '', 7)

                pdf.cell(2, 1, red[0], 0, 0, 'C')
                pdf.cell(6, 1, self.broj_karaktera(self.zamena_slova(red[1]), 35), 0, 0, 'L')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[2], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[3], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[5], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[6], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[7], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[8], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[9], grouping=True), 0, 1, 'R')

                if redovi_po_strani == 16:
                    pdf.accept_page_break()
                    pdf.add_page()
                    pdf.cell(28, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
                    redovi_po_strani = 0

                redovi_po_strani += 1
                # ukupan_broj_redova += 1

            # Ukupno za nalog
            pdf.line(1, redovi_po_strani + 1, 27, redovi_po_strani + 1)
            pdf.ln(2)

            # pdf.cell(5, 1, kontirao, 0, 1, 'C')
            pdf.output('zakljucni.pdf', 'F')

            webbrowser.open_new(r'zakljucni.pdf')

    def stampa_dnevnik(self, rezultat_stavke, pocetni, krajnji):

        locale.setlocale(locale.LC_ALL, 'de_DE')
        pdf = PDF('portrait', 'cm', 'A4')
        pdf.add_page()

        today = date.today()
        danasnji_datum = today.strftime("%d.%m.%Y")
        pdf.set_font('Helvetica', '', 11)
        # pdf.cell(13, 1, firma, 0, 0, 'L')
        pdf.cell(16, 1, 'Datum stampe:', 0, 0, 'R')
        pdf.cell(3, 1, danasnji_datum + ".", 0, 1, 'L')
        # pdf.cell(19, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(19, 1, 'DNEVNIK KNJIZENJA', 0, 1, 'C')
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(19, 1, 'za period od '+pocetni.strftime("%d.%m.%Y") + ". do " + krajnji.strftime("%d.%m.%Y")+".", 0, 1, 'C')
        pdf.set_font('Helvetica', '', 10)
        # pdf.line(1, 5, 20, 5)
        pdf.set_fill_color(221, 221, 221)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(2, 1, 'Broj naloga', 0, 0, 'C', fill=True)
        pdf.cell(3, 1, 'Vrsta naloga', 0, 0, 'C', fill=True)
        pdf.cell(2, 1, 'Datum Naloga', 0, 0, 'C', fill=True)
        pdf.cell(3, 1, 'Konto', 0, 0, 'C', fill=True)
        pdf.cell(5, 1, 'Naziv konta', 0, 0, 'C', fill=True)
        pdf.cell(2, 1, 'Duguje', 0, 0, 'C', fill=True)
        pdf.cell(2, 1, 'Potrazuje', 0, 1, 'C', fill=True)
        # pdf.line(1, 6, 20, 6)
        pdf.set_font('Helvetica', '', 8)

        redovi_po_strani = 7
        prethodni_red = ''
        nalog_duguje = 0
        nalog_potrazuje = 0
        # ukupno elemenata u rezultatu treba zbog racunanja sume poslednjeg naloga u dnevniku
        ukupno_elemenata_u_rezultatu = 0
        for red in rezultat_stavke:
            ukupno_elemenata_u_rezultatu += 1
            if red[0] != prethodni_red and prethodni_red != '':
                pdf.set_font('Helvetica', 'B', 8)
                pdf.cell(2, 1, '', 0, 0, 'C', fill=True)
                pdf.cell(3, 1, '', 0, 0, 'C', fill=True)
                pdf.cell(2, 1, '', 0, 0, 'C', fill=True)
                pdf.cell(3, 1, '', 0, 0, 'L', fill=True)
                pdf.cell(5, 1, 'Ukupno za ' + self.broj_karaktera(self.zamena_slova(prethodni_red), 20) + ':', 0, 0, 'L', fill=True)
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_duguje, grouping=True), 0, 0, 'R', fill=True)
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_potrazuje, grouping=True), 0, 1, 'R', fill=True)
                # pdf.line(1, redovi_po_strani + 1, 20, redovi_po_strani + 1)
                # pdf.line(1, redovi_po_strani + 2, 20, redovi_po_strani + 2)
                redovi_po_strani += 1
                nalog_duguje = 0
                nalog_potrazuje = 0

            pdf.set_font('Helvetica', '', 8)
            pdf.cell(2, 0.7, self.broj_karaktera(self.zamena_slova(red[0]), 12), 0, 0, 'C')
            pdf.cell(3, 0.7, self.zamena_slova(red[2]), 0, 0, 'C')
            pdf.cell(2, 0.7, red[1].strftime("%d.%m.%Y"), 0, 0, 'C')
            pdf.cell(3, 0.7, self.broj_karaktera(self.zamena_slova(red[3]), 17), 0, 0, 'L')
            pdf.cell(5, 0.7, self.broj_karaktera(self.zamena_slova(red[4]), 28), 0, 0, 'L')
            if red[6] == 'd':
                nalog_duguje += red[5]
                pdf.cell(2, 0.7, locale.format_string('%10.2f', red[5], grouping=True), 0, 0, 'R')
                pdf.cell(2, 0.7, '', 0, 1, 'R')
            else:
                nalog_potrazuje += red[5]
                pdf.cell(2, 0.7, '', 0, 0, 'R')
                pdf.cell(2, 0.7, locale.format_string('%10.2f', red[5], grouping=True), 0, 1, 'R')

            # ovaj if mora da bi se sabrao poslednji nalog u izvestaju
            if ukupno_elemenata_u_rezultatu == len(rezultat_stavke):
                pdf.set_font('Helvetica', 'B', 8)
                pdf.cell(2, 1, '', 0, 0, 'C', fill=True)
                pdf.cell(3, 1, '', 0, 0, 'C', fill=True)
                pdf.cell(2, 1, '', 0, 0, 'C', fill=True)
                pdf.cell(3, 1, '', 0, 0, 'L', fill=True)
                pdf.cell(5, 1, 'Ukupno za ' + self.broj_karaktera(self.zamena_slova(prethodni_red), 20) + ':', 0, 0, 'L', fill=True)
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_duguje, grouping=True), 0, 0, 'R', fill=True)
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_potrazuje, grouping=True), 0, 1, 'R', fill=True)
                # pdf.line(1, redovi_po_strani + 2, 20, redovi_po_strani + 2)
                # pdf.line(1, redovi_po_strani + 3, 20, redovi_po_strani + 3)

            # prethodni red je potreban da bi se poredilo da li je poceno novi nalog u petlji zbog racunanja sume prethodnog naloga
            prethodni_red = red[0]
            redovi_po_strani += 1

        # pdf.cell(5, 1, kontirao, 0, 1, 'C')
        pdf.output('dnevnik.pdf', 'F')

        webbrowser.open_new(r'dnevnik.pdf')

    def stampa_dnevnik_stari(self, rezultat_stavke, pocetni, krajnji):

        locale.setlocale(locale.LC_ALL, 'de_DE')
        pdf = FPDF('P', 'cm', 'A4')
        pdf.accept_page_break()
        pdf.add_page()

        # Prvo se u tabeli aplikacija trazi sifra korisnika koju sam uneo na pocetnom ekranu u delu podesavanja
        conn_aplikacija = AplikacijaController()
        pronadjena_aplikacija = conn_aplikacija.find()
        id_korisnika = pronadjena_aplikacija[0][1]
        # Pomocu sifre korisnika u tabeli aplikacija trazim naziv firme i (ime i prezime korisnika)
        conn_korisnik = KorisnikController()
        pronadjen_korisnik = conn_korisnik.find(id_korisnika)
        # Naziv firme
        naziv = pronadjen_korisnik[0][2]
        firma = self.zamena_slova(naziv)
        today = date.today()
        danasnji_datum = today.strftime("%d.%m.%Y")
        pdf.set_font('Arial', '', 11)
        pdf.cell(13, 1, firma, 0, 0, 'L')
        pdf.cell(3, 1, 'Datum stampe:', 0, 0, 'L')
        pdf.cell(3, 1, danasnji_datum, 0, 1, 'R')
        pdf.cell(19, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(19, 1, 'DNEVNIK KNJIZENJA', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(19, 1, 'za period od '+pocetni.strftime("%d.%m.%Y") + ". do " + krajnji.strftime("%d.%m.%Y")+".", 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.line(1, 5, 20, 5)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(2, 1, 'Broj naloga', 0, 0, 'C')
        pdf.cell(3, 1, 'Vrsta naloga', 0, 0, 'C')
        pdf.cell(2, 1, 'Datum Naloga', 0, 0, 'C')
        pdf.cell(3, 1, 'Konto', 0, 0, 'C')
        pdf.cell(5, 1, 'Naziv konta', 0, 0, 'C')
        pdf.cell(2, 1, 'Duguje', 0, 0, 'C')
        pdf.cell(2, 1, 'Potrazuje', 0, 1, 'C')
        pdf.line(1, 6, 20, 6)
        pdf.set_font('Arial', '', 8)

        redovi_po_strani = 7
        prethodni_red = ''
        nalog_duguje = 0
        nalog_potrazuje = 0
        # ukupno elemenata u rezultatu treba zbog racunanja sume poslednjeg naloga u dnevniku
        ukupno_elemenata_u_rezultatu = 0
        for red in rezultat_stavke:
            ukupno_elemenata_u_rezultatu += 1
            if red[0] != prethodni_red and prethodni_red != '':
                pdf.set_font('Arial', 'B', 8)
                pdf.cell(2, 1, '', 0, 0, 'C')
                pdf.cell(3, 1, '', 0, 0, 'C')
                pdf.cell(2, 1, '', 0, 0, 'C')
                pdf.cell(3, 1, '', 0, 0, 'L')
                pdf.cell(5, 1, 'Ukupno za ' + prethodni_red + ':', 0, 0, 'L')
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_duguje, grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_potrazuje, grouping=True), 0, 1, 'R')
                pdf.line(1, redovi_po_strani + 1, 20, redovi_po_strani + 1)
                pdf.line(1, redovi_po_strani + 2, 20, redovi_po_strani + 2)
                redovi_po_strani += 1
                nalog_duguje = 0
                nalog_potrazuje = 0

            pdf.set_font('Arial', '', 8)
            pdf.cell(2, 1, red[0], 0, 0, 'C')
            pdf.cell(3, 1, self.zamena_slova(red[2]), 0, 0, 'C')
            pdf.cell(2, 1, red[1].strftime("%d.%m.%Y"), 0, 0, 'C')
            pdf.cell(3, 1, self.broj_karaktera(self.zamena_slova(red[3]), 17), 0, 0, 'L')
            pdf.cell(5, 1, self.broj_karaktera(self.zamena_slova(red[4]), 35), 0, 0, 'L')
            if red[6] == 'd':
                nalog_duguje += red[5]
                pdf.cell(2, 1, locale.format_string('%10.2f', red[5], grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, '', 0, 1, 'R')
            else:
                nalog_potrazuje += red[5]
                pdf.cell(2, 1, '', 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', red[5], grouping=True), 0, 1, 'R')

            # ovaj if mora da bi se sabrao poslednji nalog u izvestaju
            if ukupno_elemenata_u_rezultatu == len(rezultat_stavke):
                pdf.set_font('Arial', 'B', 8)
                pdf.cell(2, 1, '', 0, 0, 'C')
                pdf.cell(3, 1, '', 0, 0, 'C')
                pdf.cell(2, 1, '', 0, 0, 'C')
                pdf.cell(3, 1, '', 0, 0, 'L')
                pdf.cell(5, 1, 'Ukupno za ' + prethodni_red + ':', 0, 0, 'L')
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_duguje, grouping=True), 0, 0, 'R')
                pdf.cell(2, 1, locale.format_string('%10.2f', nalog_potrazuje, grouping=True), 0, 1, 'R')
                pdf.line(1, redovi_po_strani + 2, 20, redovi_po_strani + 2)
                pdf.line(1, redovi_po_strani + 3, 20, redovi_po_strani + 3)

            if redovi_po_strani >= 24:
                pdf.accept_page_break()
                pdf.add_page()
                pdf.cell(19, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
                redovi_po_strani = 0
            # prethodni red je potreban da bi se poredilo da li je poceno novi nalog u petlji zbog racunanja sume prethodnog naloga
            prethodni_red = red[0]
            redovi_po_strani += 1

        pdf.ln(2)

        # pdf.cell(5, 1, kontirao, 0, 1, 'C')
        pdf.output('dnevnik.pdf', 'F')

        webbrowser.open_new(r'dnevnik.pdf')

    def stampa_glavne_knjige(self, rezultat, pocetni, krajnji):
        # Ako nema rezultata u okviru trazenog datuma da ne radi nista
        if rezultat is not None:
            locale.setlocale(locale.LC_ALL, 'de_DE')

            pdf = PDF('landscape', 'cm', 'A4')
            pdf.add_page()

            today = date.today()
            danasnji_datum = today.strftime("%d.%m.%Y")
            od_datuma = pocetni.strftime("%d.%m.%Y")
            do_datuma = krajnji.strftime("%d.%m.%Y")
            pdf.set_font('Helvetica', '', 11)
            # pdf.cell(20, 1, firma, 0, 0, 'L')
            pdf.cell(24, 1, 'Datum stampe:', 0, 0, 'R')
            pdf.cell(4, 1, danasnji_datum + ".", 0, 1, 'L')
            # pdf.cell(28, 1, 'Strana: ' + str(pdf.page_no()), 0, 1, 'R')
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(28, 1, 'GLAVNA KNJIGA', 0, 1, 'C')
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(28, 1, 'za period: ' + od_datuma + '. do ' + do_datuma + '.', 0, 1, 'C')
            pdf.set_font('Helvetica', '', 10)
            # pdf.line(1, 5, 28, 5)
            konto = ''
            suma_duguje = 0
            suma_potrazuje = 0
            prethodni_saldo = 0
            brojac = 0
            broj_elemenata_rezultata = len(rezultat)
            for red in rezultat:
                if red[0] != konto:
                    if brojac != 0:
                        pdf.set_fill_color(221, 221, 221)
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(4, 0.6, '', 0, 0, 'C', fill=True)
                        pdf.cell(4, 0.6, 'Ukupno saldo:', 0, 0, 'C', fill=True)
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', suma_duguje, grouping=True), 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', suma_potrazuje, grouping=True), 0, 0, 'R', fill=True)
                        suma_saldo = suma_duguje - suma_potrazuje
                        if suma_saldo > 0:
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', suma_saldo, grouping=True), 0, 0, 'R', fill=True)
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R', fill=True)
                            suma_duguje = 0
                            suma_potrazuje = 0
                        elif suma_saldo < 0:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R', fill=True)
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', abs(suma_saldo), grouping=True), 0, 1, 'R', fill=True)
                            suma_duguje = 0
                            suma_potrazuje = 0
                        else:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R', fill=True)
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R', fill=True)
                            suma_duguje = 0
                            suma_potrazuje = 0

                    if pdf.get_y() > 16.7:
                        pdf.add_page()
                        pdf.cell(28, 1.2, self.zamena_slova(red[0]) + "  -  " + self.zamena_slova(red[1]), 0, 1, 'L')
                        pdf.set_fill_color(221, 221, 221)
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(4, 0.6, 'Tip naloga', 0, 0, 'C', fill=True)
                        pdf.cell(4, 0.6, 'Broj naloga', 0, 0, 'C', fill=True)
                        pdf.cell(5, 0.6, 'Duguje', 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, 'Potrazuje', 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, 'Saldo duguje', 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, 'Saldo potrazuje', 0, 1, 'R', fill=True)
                    else:
                        pdf.cell(28, 1.2, self.zamena_slova(red[0]) + "  -  " + self.zamena_slova(red[1]), 0, 1, 'L')
                        pdf.set_fill_color(221, 221, 221)
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(4, 0.6, 'Tip naloga', 0, 0, 'C', fill=True)
                        pdf.cell(4, 0.6, 'Broj naloga', 0, 0, 'C', fill=True)
                        pdf.cell(5, 0.6, 'Duguje', 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, 'Potrazuje', 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, 'Saldo duguje', 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, 'Saldo potrazuje', 0, 1, 'R', fill=True)

                    pdf.set_font('Helvetica', '', 10)
                    pdf.cell(4, 0.6, self.zamena_slova(red[2]), 0, 0, 'L')
                    pdf.cell(4, 0.6, self.zamena_slova(red[3]), 0, 0, 'L')
                    if red[5] == "d":
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                        pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                        pdf.cell(5, 0.6, '0.00', 0, 1, 'R')
                        suma_duguje += red[4]
                        prethodni_saldo = red[4]
                    else:
                        pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                        pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', red[4], grouping=True), 0, 1, 'R')
                        suma_potrazuje += red[4]
                        prethodni_saldo = -red[4]
                else:
                    pdf.set_font('Helvetica', '', 10)
                    pdf.cell(4, 0.6, self.zamena_slova(red[2]), 0, 0, 'L')
                    pdf.cell(4, 0.6, self.zamena_slova(red[3]), 0, 0, 'L')
                    if red[5] == "d":
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                        pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                        saldo_reda = red[4] + prethodni_saldo
                        if saldo_reda > 0:
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', abs(saldo_reda), grouping=True), 0, 0, 'R')
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R')
                            suma_duguje += red[4]
                            prethodni_saldo = saldo_reda
                        elif saldo_reda < 0:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', abs(saldo_reda), grouping=True), 0, 1, 'R')
                            suma_duguje += red[4]
                            prethodni_saldo = saldo_reda
                        else:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R')
                            suma_duguje += red[4]
                            prethodni_saldo = saldo_reda
                    else:
                        pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', red[4], grouping=True), 0, 0, 'R')
                        saldo_reda = -red[4] + prethodni_saldo
                        if saldo_reda > 0:
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', abs(saldo_reda), grouping=True), 0, 0, 'R')
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R')
                            suma_potrazuje += red[4]
                            prethodni_saldo = saldo_reda
                        elif saldo_reda < 0:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', abs(saldo_reda), grouping=True), 0, 1, 'R')
                            suma_potrazuje += red[4]
                            prethodni_saldo = saldo_reda
                        else:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R')
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R')
                            suma_potrazuje += red[4]
                            prethodni_saldo = saldo_reda

                    # ovo mora zbog prikaza sume poslednjeg konta u nizu
                    if brojac + 1 == broj_elemenata_rezultata:
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(4, 0.6, '', 0, 0, 'C', fill=True)
                        pdf.cell(4, 0.6, 'Ukupno saldo:', 0, 0, 'C', fill=True)
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', suma_duguje, grouping=True), 0, 0, 'R', fill=True)
                        pdf.cell(5, 0.6, locale.format_string('%10.2f', suma_potrazuje, grouping=True), 0, 0, 'R', fill=True)
                        suma_saldo = suma_duguje - suma_potrazuje
                        if suma_saldo > 0:
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', suma_saldo, grouping=True), 0, 0, 'R', fill=True)
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R', fill=True)
                            suma_duguje = 0
                            suma_potrazuje = 0
                        elif suma_saldo < 0:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R', fill=True)
                            pdf.cell(5, 0.6, locale.format_string('%10.2f', abs(suma_saldo), grouping=True), 0, 1, 'R', fill=True)
                            suma_duguje = 0
                            suma_potrazuje = 0
                        else:
                            pdf.cell(5, 0.6, '0.00', 0, 0, 'R', fill=True)
                            pdf.cell(5, 0.6, '0.00', 0, 1, 'R', fill=True)
                            suma_duguje = 0
                            suma_potrazuje = 0

                brojac += 1
                konto = red[0]

            pdf.output('glavna_knjiga.pdf', 'F')

            webbrowser.open_new(r'glavna_knjiga.pdf')

    def zakljucni_list_excel(self, podaci, pocetni, krajnji):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('zakljucni_list_excel.xlsx')
        worksheet = workbook.add_worksheet()
        # FORMATIRANJE
        # Add a bold format to use to highlight cells.
        cell_format = workbook.add_format({'valign': 'center', 'border': 1})
        cell_format.set_text_wrap()
        # Add a number format for cells
        # money = workbook.add_format({'num_format': '#,##0.00'})
        zaglavlje = workbook.add_format({'valign': 'center', 'bold': True, 'bg_color': '#99c7f7'})
        zaglavlje_naslov = workbook.add_format({'valign': 'center', 'bold': True})
        # zaglavlje_datum = workbook.add_format({'valign': 'center', 'num_format': 'dd.mm.yyyy.'})
        # zaglavlje_novac = workbook.add_format({'valign': 'center', 'num_format': '#,##0.00'})
        # naslov = workbook.add_format({'valign': 'center', 'font': {'name': 'Arial', 'size': 16}, 'bold': True})
        zaglavlje_tabele_nazivi = workbook.add_format({'valign': 'center', 'bottom': 1, 'bg_color': '#99c7f7'})
        # tabela_cell_format
        tabela_money = workbook.add_format({'num_format': '#,##0.00', 'bottom': 1})
        tabela_konta = workbook.add_format({'valign': 'center', 'bottom': 1})
        tabela_naziv_konta = workbook.add_format({'valign': 'left', 'bottom': 1})

        # ZAGLAVLJE TABELE
        # Pravljenje zaglavlja tabele
        od_datuma = pocetni.strftime("%d.%m.%Y.")
        do_datuma = krajnji.strftime("%d.%m.%Y.")
        period = 'za period: ' + od_datuma + ' do ' + do_datuma
        worksheet.merge_range(0, 0, 0, 9, 'ZAKLJUČNI LIST', zaglavlje_naslov)
        worksheet.merge_range(1, 0, 1, 9, period, zaglavlje_naslov)
        worksheet.write(2, 0, '', zaglavlje)
        worksheet.write(2, 1, '', zaglavlje)
        worksheet.merge_range(2, 2, 2, 3, 'Početno stanje', zaglavlje)
        worksheet.merge_range(2, 4, 2, 5, 'Tekući promet', zaglavlje)
        worksheet.merge_range(2, 6, 2, 7, 'Ukupan promet', zaglavlje)
        worksheet.merge_range(2, 8, 2, 9, 'Saldo', zaglavlje)
        worksheet.write(3, 0, 'Konto', zaglavlje_tabele_nazivi)
        worksheet.write(3, 1, 'Naziv konta', zaglavlje_tabele_nazivi)
        worksheet.write(3, 2, 'Duguje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 3, 'Potražuje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 4, 'Duguje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 5, 'Potražuje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 6, 'Duguje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 7, 'Potražuje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 8, 'Duguje', zaglavlje_tabele_nazivi)
        worksheet.write(3, 9, 'Potražuje', zaglavlje_tabele_nazivi)
        row = 4

        for konto, naziv_konta, ps_duguje, ps_potrazuje, tp_duguje, tp_potrazuje, up_duguje, up_potrazuje, sal_duguje, sal_potrazuje in podaci:
            worksheet.write(row, 0, konto, tabela_konta)
            worksheet.write(row, 1, naziv_konta, tabela_naziv_konta)
            worksheet.write(row, 2, ps_duguje, tabela_money)
            worksheet.write(row, 3, ps_potrazuje, tabela_money)
            worksheet.write(row, 4, tp_duguje, tabela_money)
            worksheet.write(row, 5, tp_potrazuje, tabela_money)
            worksheet.write(row, 6, up_duguje, tabela_money)
            worksheet.write(row, 7, up_potrazuje, tabela_money)
            worksheet.write(row, 8, sal_duguje, tabela_money)
            worksheet.write(row, 9, sal_potrazuje, tabela_money)
            row += 1

        # Autofit the worksheet.
        worksheet.autofit()
        workbook.close()
        os.startfile('zakljucni_list_excel.xlsx')

    def stampa_efakture(self, poruka_zaglavlje1, poruka_zaglavlje2, datum_izdavanja, broj_fakture, broj_ugovora, datum_prometa, datum_dospeca, jbkjs, maticni_broj_kupca, pib_kupca, naziv_kupca, adresa_kupca, grad_kupca, broj_poste_kupca, valuta_fakture, iznos_za_placanje, naziv_dobavljaca, pib_dobavljaca, adresa_dobavljaca, grad_dobavljaca, broj_poste_dobavljaca, tekuci_racun_dobavljaca, maticni_broj_dobavljaca, spisak_artikala, porezi):
        locale.setlocale(locale.LC_ALL, 'de_DE')
        pdf = STAMPA('portrait', 'cm', 'A4')
        # pdf.accept_page_break()
        pdf.add_page()
        datum = datum_izdavanja.strftime("%d.%m.%Y.")
        datum_prom = datum_prometa.strftime("%d.%m.%Y.")
        datum_dosp = datum_dospeca.strftime("%d.%m.%Y.")
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(19, 0.5, poruka_zaglavlje1, 0, 1, 'C')
        pdf.cell(19, 0.5, poruka_zaglavlje2, 0, 1, 'C')
        pdf.cell(19, 2, "", 0, 1, 'C')
        pdf.cell(3, 0.5, 'Datum izdavanja:', 0, 0, 'L')
        pdf.cell(3, 0.5, datum, 0, 0, 'L')
        pdf.cell(4, 0.5, "", 0, 0)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(192, 192, 192)
        pdf.cell(9, 0.5, 'Broj fakture ', 0, 1, 'C', fill=True)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(10, 0.4, "", 0, 0)
        pdf.cell(9, 0.4, self.zamena_slova(broj_fakture), 0, 1, 'C')
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(19, 0.4, self.broj_karaktera(self.zamena_slova(naziv_kupca), 40), 0, 1, 'L')
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(10, 0.4, self.zamena_slova(adresa_kupca), 0, 0, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(4, 0.4, 'Broj ugovora', 0, 0, 'R')
        pdf.cell(5, 0.4, self.zamena_slova(broj_ugovora), 0, 1, 'L')
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(10, 0.4, self.zamena_slova(broj_poste_kupca) + self.zamena_slova(grad_kupca), 0, 0, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(4, 0.4, 'Datum prometa', 0, 0, 'R')
        pdf.cell(5, 0.4, datum_prom, 0, 1, 'L')
        pdf.cell(10, 0.4, '', 0, 0)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(4, 0.4, 'Datum dospeca', 0, 0, 'R')
        pdf.cell(5, 0.4, datum_dosp, 0, 1, 'L')
        pdf.cell(10, 0.4, '', 0, 0)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(4, 0.4, 'JBKJS', 0, 0, 'R')
        pdf.cell(5, 0.4, jbkjs, 0, 1, 'L')
        pdf.cell(10, 0.4, '', 0, 0)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(4, 0.4, 'Maticni broj kupca', 0, 0, 'R')
        pdf.cell(5, 0.4, maticni_broj_kupca, 0, 1, 'L')
        pdf.cell(10, 0.4, '', 0, 0)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(4, 0.4, 'PIB kupca', 0, 0, 'R')
        pdf.cell(5, 0.4, pib_kupca, 0, 1, 'L')
        pdf.cell(10, 0.4, '', 0, 0)
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(4, 0.4, 'Valuta fakture', 0, 0, 'R')
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(5, 0.4, self.zamena_slova(valuta_fakture), 0, 1, 'L')
        pdf.cell(10, 0.4, '', 0, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(4, 0.4, 'Iznos fakture', 0, 0, 'R')
        pdf.cell(5, 0.4, locale.format_string('%10.2f', float(iznos_za_placanje), grouping=True), 0, 1, 'L')
        pdf.cell(19, 2, '', 0, 1)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(19, 0.5, 'Prodavac', 0, 1)
        pdf.line(1, 11, 20, 11)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(19, 0.5, self.zamena_slova(naziv_dobavljaca), 0, 1, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(14, 0.5, "Adresa: " + self.zamena_slova(broj_poste_dobavljaca) + " " + self.zamena_slova(grad_dobavljaca) + " " + self.zamena_slova(adresa_dobavljaca), 0, 0, 'L')
        pdf.cell(5, 0.5, self.zamena_slova(tekuci_racun_dobavljaca), 0, 1, 'R')
        pdf.cell(19, 0.5, "Maticni broj: " + maticni_broj_dobavljaca, 0, 1, 'L')
        pdf.cell(19, 0.5, "PIB: " + pib_dobavljaca, 0, 1, 'L')
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(7, 0.5, 'Opis', 0, 0, 'L', fill=True)
        pdf.cell(2, 0.5, 'Kolicina', 0, 0, 'R', fill=True)
        pdf.cell(2, 0.5, 'Jed.cena', 0, 0, 'R', fill=True)
        pdf.cell(2, 0.5, 'Jed.mere', 0, 0, 'R', fill=True)
        pdf.cell(2, 0.5, 'Umanjenje', 0, 0, 'R', fill=True)
        pdf.cell(2, 0.5, 'Iznos bez PDV', 0, 0, 'R', fill=True)
        pdf.cell(2, 0.5, 'PDV stopa', 0, 1, 'R', fill=True)
        # tabela sa pojedinacnim artiklima
        pdf.set_font('Helvetica', '', 7)
        # ovde se ispisuje ukupan iznos fakture - prvi deo totala
        for artikal in spisak_artikala:
            pdf.cell(7, 0.5, self.broj_karaktera(self.zamena_slova(artikal[0]), 35), 0, 0, 'L')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(artikal[1]), grouping=True), 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(artikal[2]), grouping=True), 0, 0, 'R')
            pdf.cell(2, 0.5, self.zamena_slova(artikal[3]), 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(artikal[4]), grouping=True), 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(artikal[5]), grouping=True), 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(artikal[6]), grouping=True), 0, 1, 'R')
            pdf.cell(7, 0.5, "Sifra " + self.zamena_slova(artikal[7]), 0, 1, 'L')
        for stavka in porezi:
            pdf.cell(17, 0.5, f"Zbir stavki sa stopom {stavka[1]}%: ", 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(stavka[2]), grouping=True), 0, 1, 'R')
            pdf.cell(17, 0.5, f"Ukupna osnovica - stopa {stavka[1]}%: ", 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(stavka[2]), grouping=True), 0, 1, 'R')
            pdf.cell(17, 0.5, f"Ukupan PDV - stopa {stavka[1]}%: ", 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(stavka[0]), grouping=True), 0, 1, 'R')
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(17, 0.5, f"Ukupan iznos fakture: ", 0, 0, 'R')
            pdf.cell(2, 0.5, locale.format_string('%10.2f', float(iznos_za_placanje), grouping=True), 0, 1, 'R')
        # ovde se ispisuje vrednost avansa ako ga ima - drugi deo fakture


        # ovde se ispisuje iznos za placanje - treci deo fakture


        pdf.output('efaktura.pdf', 'F')

        webbrowser.open_new(r'efaktura.pdf')



