from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske

# Connect to database
class KontoController:

    tablename = "konto"

    def read(self):
        try:
            select_columns = "*"
            order = 'oznaka'
            connection = Database()
            sve_konto = connection.select(self.tablename, select_columns, order)
            return sve_konto
        except Error as e:
            Greske("Greska citanje svih konta - KontoController", e)

    def read_condition(self):
        try:
            select_columns = "*"
            order = 'oznaka'
            condition = 'vrsta'
            value = 'subanalitika'
            connection = Database()
            sve_konto = connection.select_where(self.tablename, select_columns, condition, value, order)
            return sve_konto
        except Error as e:
            Greske("Citanje konta subanalitika - KontoController", e)

    def update_konto(self, konto, naziv, konto_id):
        # Ažuriranje baze podataka
        try:
            set_condition = 'oznaka="{}"'.format(konto)+', naziv="{}"'.format(naziv)
            filter_condition = ' idkonto='+konto_id
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska prilikom azuriranje konta - KontoController", e)

    def insert_konto(self, konto, naziv, vrsta):
        try:
            schema = "oznaka, naziv, vrsta"
            value = (konto, naziv, vrsta)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska unos konta - KontoController", e)

    # Brisanje iz baze podataka
    def delete_konto(self, konto_id):
        try:
            delete_condition = "idkonto="+konto_id
            connection = Database()
            connection.delete(self.tablename, delete_condition)
        except Error as e:
            Greske("Greska brisanje konta - KontoController", e)

    def pronadji_poslednji_konto(self):
        try:
            select_columns = "idkonto"
            order = 'idkonto'
            connection = Database()
            poslednji_konto = connection.select_last_row(self.tablename, select_columns, order)
            return poslednji_konto
        except Error as e:
            Greske("Greska pronalazenje poslednjeg konta - KontoController", e)

    # Provera u bazi da li vec postoji unet konto
    def check_konto_exist(self, oznaka_konta):
        try:
            where_columns = "oznaka"
            value = oznaka_konta
            connection = Database()
            rezultat = connection.select_count(self.tablename, where_columns, value)
            if rezultat[0][0] == 0:
                return False
            else:
                return True
        except Error as e:
            Greske("Greska provera da li postoji konto - KontoController", e)

    def find(self, oznaka_konta):
        try:
            select_columns = "*"
            # order = 'oznaka'
            condition = 'oznaka'
            value = oznaka_konta
            connection = Database()
            sve_konto = connection.select_where(self.tablename, select_columns, condition, value)
            return sve_konto
        except Error as e:
            Greske("Greska pronalazenje konta po oznaci - KontoController", e)

    def find_oznaka(self, oznaka_konta):
        try:
            select_columns = "naziv"
            condition = 'oznaka'
            value = oznaka_konta
            connection = Database()
            sve_konto = connection.select_where(self.tablename, select_columns, condition, value)
            return sve_konto
        except Error as e:
            Greske("Greska pronalazenje konta po oznaci - KontoController", e)

    def find_id(self, konto_id):
        try:
            select_columns = "*"
            condition = 'idkonto'
            value = konto_id
            connection = Database()
            sve_konto = connection.select_where(self.tablename, select_columns, condition, value)
            return sve_konto
        except Error as e:
            Greske("Greska pronalazenje konta po oznaci - KontoController", e)

    def deo_konta_postoji(self, deo_konta):
        try:
            condition = 'oznaka'
            value = deo_konta
            connection = Database()
            sve_stavke = connection.select_like(self.tablename, condition, value)
            return sve_stavke
        except Error as e:
            Greske("Deo konta postoji u stavkama - StavkaNalogaController", e)

    # Dobijanje kartice konta
    def kartica_konta(self, konto_id, datum_pocetni, datum_krajnji):
        try:
            select_columns = "nalog.nalogID, nalog.broj, nalog.datum, stavke_naloga.iznos, stavke_naloga.status_dp"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID='{}'".format(
                konto_id) + "and nalog.proknjizen='da' and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            order_by = "nalog.datum"
            connection = Database()
            sve_konto = connection.select_where_join(select_columns, iz_tabele, join1, join2, where_condition,
                                                     order_by)
            return sve_konto
        except Error as e:
            Greske("Dobijanje kartice konta - KontoController", e)

    # Dobijanje rezultata za stanje konta po kategorijama
    def stanje_konta_kategorije(self, kategorija_num, datum_pocetni, datum_krajnji):
        try:
            select_columns = "sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='p' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos else -stavke_naloga.iznos end)"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and nalog.proknjizen='da' and nalog.datum between '{}'".format(datum_pocetni)+" and '{}'".format(datum_krajnji)
            nivo = kategorija_num
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct(select_columns, iz_tabele,  join1, join2, where_condition, order_by, nivo)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po kategorijama - KontoController", e)

    # Dobijanje rezultata za stanje konta po subanalitici
    def stanje_kategorije_subanalitika(self, datum_pocetni, datum_krajnji):
        try:
            select_columns = "sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='p' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos else -stavke_naloga.iznos end)"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and nalog.proknjizen='da' and konto.vrsta='subanalitika' and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct(select_columns, iz_tabele, join1, join2, where_condition,
                                                   order_by)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po subanalitici - KontoController", e)

    # Dobijanje pomocne knjige dobavljaca
    def knjiga_dobavljaca_spisak(self, datum_pocetni, datum_krajnji):
        try:
            select_columns = "sum(case when stavke_naloga.status_dp='d' and nalog.vrsta='Početno stanje' then ifnull(stavke_naloga.iznos, 0) end), sum(case when stavke_naloga.status_dp='p' and nalog.vrsta='Početno stanje' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='d' and nalog.vrsta <> 'Početno stanje' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='p' and nalog.vrsta <> 'Početno stanje' then stavke_naloga.iznos end)"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and nalog.proknjizen='da' and konto.oznaka like '252111-%' and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct_dobavljaci(select_columns, iz_tabele, join1, join2,
                                                              where_condition, order_by)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po subsubanalitici - KontoController", e)

    # Dobijanje pomocne knjige placenih avansa
    def knjiga_placeni_avansi(self, datum_pocetni, datum_krajnji):
        try:
            select_columns = "sum(case when stavke_naloga.status_dp='d' and nalog.vrsta='Početno stanje' then ifnull(stavke_naloga.iznos, 0) end), sum(case when stavke_naloga.status_dp='p' and nalog.vrsta='Početno stanje' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='d' and nalog.vrsta <> 'Početno stanje' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='p' and nalog.vrsta <> 'Početno stanje' then stavke_naloga.iznos end)"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and nalog.proknjizen='da' and (konto.oznaka like '123221-%' or konto.oznaka like '123231-%' or konto.oznaka like '123231-%') and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct_dobavljaci(select_columns, iz_tabele, join1, join2,
                                                              where_condition, order_by)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po subsubanalitici - KontoController", e)

    # Dobijanje rezultata za stanje konta po subsubanalitici
    def stanje_kategorije_subsubanalitika(self, datum_pocetni, datum_krajnji):
        try:
            select_columns = "sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='p' then stavke_naloga.iznos end), sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos else -stavke_naloga.iznos end)"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and nalog.proknjizen='da' and length(konto.oznaka) > 6 and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct(select_columns, iz_tabele, join1, join2, where_condition, order_by)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po subsubanalitici - KontoController", e)

    # Dobijanje rezultata za stanje konta po kategorijama
    def izvrsenje_budzeta(self, kategorija_num, datum_pocetni, datum_krajnji, izvori):
        try:
            select_columns = []
            for izvor in izvori:
                select_columns += ["sum(case when stavke_naloga.status_dp='d' and stavke_naloga.izvor='{}'".format(izvor) + " then stavke_naloga.iznos when stavke_naloga.status_dp='p' and stavke_naloga.izvor='{}'".format(izvor) + " then -stavke_naloga.iznos end) as '{}'".format(izvor)]
            select_izjava = ", ".join(select_columns)
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and konto.oznaka between '400000' and '699999' and nalog.proknjizen='da' and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            nivo = kategorija_num
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct_izvrsenje(select_izjava, iz_tabele, join1, join2, where_condition,
                                                   order_by, nivo)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po kategorijama - KontoController", e)

    # Zakljucni list
    def zakljucni_list(self, kategorija_num, datum_pocetni, datum_krajnji, godina):
        try:
            pocetno="PS-{}".format(godina)
            select_columns = "sum(case when stavke_naloga.status_dp='d' and nalog.broj='{}'".format(pocetno)+" then stavke_naloga.iznos else 0 end) as pocetno_dug, sum(case when stavke_naloga.status_dp='p' and nalog.broj='{}'".format(pocetno)+" then stavke_naloga.iznos else 0 end) as pocetno_potr, sum(case when stavke_naloga.status_dp='d' and nalog.broj<>'{}'".format(pocetno) +" then stavke_naloga.iznos else 0 end) as tekuce_dug, sum(case when stavke_naloga.status_dp='p' and nalog.broj<>'{}'".format(pocetno)+" then stavke_naloga.iznos else 0 end) as tekuce_potr, sum(case when stavke_naloga.status_dp='d' then stavke_naloga.iznos else 0 end) as ukupno_dug, sum(case when stavke_naloga.status_dp='p' then stavke_naloga.iznos else 0 end) as ukupno_potr"
            iz_tabele = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            where_condition = "stavke_naloga.kontoID=konto.idkonto and nalog.proknjizen='da' and nalog.datum between '{}'".format(
                datum_pocetni) + " and '{}'".format(datum_krajnji)
            nivo = kategorija_num
            order_by = "konto.oznaka"
            connection = Database()
            sve_konto = connection.select_distinct(select_columns, iz_tabele, join1, join2, where_condition,
                                                   order_by, nivo)
            return sve_konto
        except Error as e:
            Greske("Dobijanje stanje konta po kategorijama - KontoController", e)
