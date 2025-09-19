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

    def read_nalozi_oris(self, godina):
        try:
            select_columns = "nalog.nalogID, nalog.broj, nalog.datum, nalog.vrsta, nalog.proknjizen, "
            case_uslov = "CASE WHEN nalog.oris_id IS NOT NULL THEN oris.broj_oris ELSE 'ne' END as formiran_oris"
            left_join = "oris ON nalog.oris_id=oris.idoris"
            condition = "EXTRACT(YEAR FROM datum)"
            value = godina
            order = "datum"
            connection = Database()
            sve_stavke = connection.select_where_case(self.tablename, select_columns, condition, value, case_uslov,
                                                      left_join, order)
            return sve_stavke
        except Error as e:
            Greske(
                "Pronalazenje u bazi spiska naloga sa podacima BEZ duguje potrazuje, i da li je proknjizen - ovo ide u tabelu na naslovnu stranu za trenutnu radnu godinu- NaloziController ",
                e)

    def read_nalozi_pravljenje_oris(self, godina):
        try:
            select_columns = "nalog.nalogID, nalog.datum, nalog.datum_knjizenja, nalog.broj"
            condition1 = "EXTRACT(YEAR FROM datum)"
            value1 = godina
            condition2 = "nalog.proknjizen"
            value2 = "da"
            condition3 = "oris_id"
            value3 = "IS NULL"
            order = "datum"
            connection = Database()
            sve_stavke = connection.select_three_where(self.tablename, select_columns, condition1, value1, condition2, value2, condition3, value3, order)
            return sve_stavke
        except Error as e:
            Greske(
                "Pronalazenje u bazi spiska naloga sa podacima BEZ duguje potrazuje, i da li je proknjizen - ovo ide u tabelu na naslovnu stranu za trenutnu radnu godinu- NaloziController ",
                e)


    '''
    def read_nalozi_oris(self, godina):
        try:
            select_columns = "nalog.nalogID, nalog.broj, nalog.datum, nalog.vrsta, nalog.proknjizen, "
            case_uslov = "CASE WHEN oris.nalog_id IS NOT NULL THEN oris.broj_oris ELSE 'ne' END as formiran_oris"
            left_join = "oris ON oris.nalog_id=nalog.nalogID"
            condition = "EXTRACT(YEAR FROM datum)"
            value = godina
            order = "datum"
            connection = Database()
            sve_stavke = connection.select_where_case(self.tablename, select_columns, condition, value, case_uslov, left_join, order)
            return sve_stavke
        except Error as e:
            Greske("Pronalazenje u bazi spiska naloga sa podacima BEZ duguje potrazuje, i da li je proknjizen - ovo ide u tabelu na naslovnu stranu za trenutnu radnu godinu- NaloziController ", e)
    '''
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
            Greske("Pronalazenje u bazi spiska naloga za dnevnik knjizenja- NaloziController.read_dnevnik_knjizenja", e)

    def update_nalog_oris(self, id_naloga, id_orisa):
        # Ažuriranje baze podataka
        try:
            set_condition = 'oris_id="{}"'.format(id_orisa)
            filter_condition = 'nalogID={}'.format(id_naloga)
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska prilikom azuriranje naloga, unosa id orisa - NaloziController.update_nalog_oris", e)