from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske


class StavkaNalogaController:
    tablename = "stavke_naloga"

    def read(self):
        try:
            select_columns = "*"
            order = 'stavkaID'
            connection = Database()
            sve_stavke = connection.select(self.tablename, select_columns, order)
            return sve_stavke
        except Error as e:
            Greske("Citanje stavki naloga - StavkaNalogaController", e)

    def insert_stavka(self, konto, izvor, nalog, iznos, status, komentar):
        try:
            schema = "kontoID, izvor, nalogID, iznos, status_dp, komentar"
            value = (konto, izvor, nalog, iznos, status, komentar)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom unosa stavke naloga - StavkaNalogaController", e)

    def update_stavka(self, konto, izvor, iznos, nalog, status, komentar, stavka_id):
        # Ažuriranje baze podataka
        try:
            set_condition = 'kontoID="{}"'.format(konto)+', izvor="{}"'.format(izvor)+', nalogID="{}"'.format(nalog)+', iznos="{}"'.format(iznos)+', status_dp="{}"'.format(status)+', komentar="{}"'.format(komentar)
            filter_condition = 'stavkaID={}'.format(stavka_id)
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska prilikom azuriranje stavke naloga - StavkaNalogaController", e)

    def delete_stavka(self, stavka_id):
        # Brisanje iz baze podataka
        try:
            delete_condition = "stavkaID='{}'".format(stavka_id)
            connection = Database()
            connection.delete(self.tablename, delete_condition)

        except Error as e:
            Greske("Greška prilikom brisanja stavke naloga! - StavkaNalogaController", e)

    def find_join(self, id_naloga):
        try:
            select_columns = "stavke_naloga.stavkaID, konto.oznaka, konto.naziv, stavke_naloga.izvor, stavke_naloga.iznos, stavke_naloga.status_dp, stavke_naloga.komentar"
            order = 'stavke_naloga.stavkaID'
            condition = 'stavke_naloga.nalogID'
            value = id_naloga
            tablenames = 'stavke_naloga, konto'
            condition2 = 'konto.idkonto'
            value2 = 'stavke_naloga.kontoID'
            connection = Database()
            sve_stavke = connection.join(tablenames, select_columns, condition, value, condition2, value2, order)
            return sve_stavke
        except Error as e:
            Greske("Greska kod selektovanja stavke naloga StavkaNalogaController", e)

    def koliko_stavki(self, id_naloga):
        try:
            condition = 'stavke_naloga.nalogID'
            value = id_naloga
            connection = Database()
            sve_stavke = connection.select_count(self.tablename, condition, value)
            return sve_stavke
        except Error as e:
            Greske("Koliko stavki naloga - StavkaNalogaController", e)

    def koliko_konta_u_stavkama(self, id_konta):
        try:
            condition = 'stavke_naloga.kontoID'
            value = id_konta
            connection = Database()
            sve_stavke = connection.select_in(self.tablename, condition, value)
            return sve_stavke
        except Error as e:
            Greske("Koliko stavki naloga - StavkaNalogaController", e)

    # pronalazenje u bazi naloga pomocu ID kako bi se uzeli podaci za taj nalog i stavke naloga koje se nalaze u njemu
    def find_stavke(self, nalog_id):
        try:
            select_columns = "*"
            condition = 'nalogID'
            value = nalog_id
            connection = Database()
            pronadjene_stavke = connection.select_where(self.tablename, select_columns, condition, value)
            return pronadjene_stavke
        except Error as e:
            Greske("Pronalazenje u bazi naloga pomocu ID kako bi se uzeli podaci za taj nalog i stavke naloga koje se nalaze u njemu", e)

    # pronalazenje svih izvora finansiranja koja postoje u tabeli stavke naloga zbog izvestaja o izvrsenju budzeta
    def pronadji_izvore(self):
        try:
            select_columns = "izvor"
            connection = Database()
            pronadjeni_izvori = connection.select_distinct_pojavljivanje(select_columns, self.tablename)
            return pronadjeni_izvori
        except Error as e:
            Greske("Pronalazenje u bazi koliko ima izvora finansiranja u tabeli stavke naloga", e)

    def prikazi_podatke_glavna_knjiga(self, pocetni_datum, krajnji_datum):
        try:
            select_columns = "konto.oznaka, konto.naziv, nalog.vrsta, nalog.broj, stavke_naloga.iznos, stavke_naloga.status_dp"
            join1 = "konto on stavke_naloga.kontoID=konto.idkonto"
            join2 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            condition = 'nalog.proknjizen="da" and nalog.datum between "{}"'.format(pocetni_datum)+' and "{}"'.format(krajnji_datum)
            order = "konto.oznaka asc, nalog.datum asc"
            connection = Database()
            pronadjene_stavke = connection.select_where_join(select_columns, self.tablename, join1, join2, condition, order)
            return pronadjene_stavke
        except Error as e:
            Greske("Pronalazenje podataka za Glavnu knjigu", e)
