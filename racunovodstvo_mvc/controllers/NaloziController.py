from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske


class NaloziController:

    tablename = "nalog"

    # Provera u bazi da li vec postoji nalog sa unetim brojem
    def check_nalog_exist(self, broj_naloga, datum):
        try:
            where_columns = "broj"
            value = broj_naloga
            where_columns2 = "YEAR(datum)"
            value2 = datum
            connection = Database()
            rezultat = connection.select_count(self.tablename, where_columns, value, where_columns2, value2)

            if rezultat[0][0] == 0:
                return False
            else:
                return True

        except Error as e:
            Greske("Hmmmm, neka greška prilikom povezivanja na bazu podataka! provera da li postoji nalog - NaloziController", e)

    # Pronalazenje u bazi spiska naloga sa podacima BEZ duguje potrazuje, i da li je proknjizen - ovo ide u tabelu na naslovnu stranu za trenutnu radnu godinu
    def read(self, godina):
        try:
            select_columns = "nalog.nalogID, nalog.broj, nalog.datum, nalog.vrsta, nalog.proknjizen"
            condition = "EXTRACT(YEAR FROM datum)"
            value = godina
            order = "datum"
            connection = Database()
            sve_stavke = connection.select_where(self.tablename, select_columns, condition, value, order)
            return sve_stavke
        except Error as e:
            Greske("Pronalazenje u bazi spiska naloga sa podacima BEZ duguje potrazuje, i da li je proknjizen - ovo ide u tabelu na naslovnu stranu za trenutnu radnu godinu- NaloziController ", e)

    # pronalazenje u bazi naloga pomocu ID kako bi se uzeli podaci za taj nalog i stavke naloga koje se unose u njega
    def find_nalog(self, id_naloga):
        try:
            select_columns = "*"
            condition = 'nalogID'
            value = id_naloga
            connection = Database()
            pronadjen_nalog = connection.select_where(self.tablename, select_columns, condition, value)
            return pronadjen_nalog
        except Error as e:
            Greske("Pronalazenje u bazi naloga pomocu ID kako bi se uzeli podaci za taj nalog i stavke naloga koje se unose u njega NaloziController ", e)

    def delete_nalog(self, id_naloga):
        # Brisanje iz baze podataka
        try:
            delete_condition = "nalogID='{}'".format(id_naloga)
            connection = Database()
            connection.delete(self.tablename, delete_condition)
        except Error as e:
            Greske("Hmmmm, neka greška prilikom brisanja naloga! - NaloziController", e)

    # pronalazenje u bazi poslednjeg unetog naloga
    def pronadji_poslednji(self):
        try:
            select_columns = "*"
            condition = 'nalogID'
            value = '(SELECT max(nalogID) FROM nalog)'
            connection = Database()
            pronadjen_nalog = connection.select_last(self.tablename, select_columns, condition, value)
            return pronadjen_nalog
        except Error as e:
            Greske("Greška prilikom povezivanja na bazu podataka! Pronalazenje u bazi poslednjeg unetog naloga - NaloziController", e)

    # Provera u bazi da li vec postoji nalog sa unetim brojem
    def provera_postoji_pocetno_u_godini(self, godina):
        try:
            where_columns = "broj"
            value = "PS-{}".format(godina)
            where_columns2 = "YEAR(datum)"
            value2 = godina
            where_columns3 = "proknjizen"
            value3 = "da"
            connection = Database()
            rezultat = connection.select_count_tree_conditions(self.tablename, where_columns, value, where_columns2, value2, where_columns3, value3)

            if rezultat[0][0] == 0:
                return False
            else:
                return True

        except Error as e:
            Greske(
                "Hmmmm, neka greška prilikom povezivanja na bazu podataka! provera da li postoji nalog - NaloziController", e)

    # Pronalazenje u bazi spiska naloga sa podacima BEZ duguje potrazuje, i da li je proknjizen - ovo ide u tabelu na naslovnu stranu za trenutnu radnu godinu
    def read_dnevnik_knjizenja(self, pocetna, krajnja):
        try:
            select_columns = "nalog.broj, nalog.datum, nalog.vrsta, konto.oznaka, konto.naziv, stavke_naloga.iznos, stavke_naloga.status_dp"
            condition = "nalog.proknjizen='da' and nalog.datum between '{}'".format(pocetna)+" and '{}'".format(krajnja)
            order = "nalog.datum"
            table = "stavke_naloga"
            join1 = "nalog on stavke_naloga.nalogID=nalog.nalogID"
            join2 = "konto on stavke_naloga.kontoID=konto.idkonto"
            connection = Database()
            sve_stavke = connection.select_where_join(select_columns, table, join1, join2, condition, order)
            return sve_stavke
        except Error as e:
            Greske("Pronalazenje u bazi spiska naloga za dnevnik knjizenja- NaloziController ", e)
