from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske


# Connect to database
class EfakturaController:

    tablename = "efakture"

    # pronalazenje u bazi eFaktura pomocu ID naloga kako bi se uzeli podaci za taj nalog i eFakture koje se nalaze u njemu
    def find_efakture(self, nalog_id):
        try:
            select_columns = "*"
            condition = 'id_naloga'
            value = nalog_id
            connection = Database()
            pronadjene_efakture = connection.select_where(self.tablename, select_columns, condition, value)
            return pronadjene_efakture
        except Error as e:
            Greske("Pronalazenje u bazi efaktura pomocu ID naloga kako bi se nasle efakture koje se nalaze u njemu - eFaktureController", e)

    # unos nove efakture
    def insert_efaktura(self, naziv, nalog_id):
        try:
            schema = "naziv, id_naloga"
            value = (naziv, nalog_id)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom unosa efakture - EfakturaController", e)

    # Brisanje iz baze podataka
    def delete_efakture(self, id_efakture):
        try:
            delete_condition = "idefakture=" + str(id_efakture)
            connection = Database()
            connection.delete(self.tablename, delete_condition)
        except Error as e:
            Greske("Greska brisanje efakture - EfakturaController", e)

    # pronalazenje u bazi eFaktura pomocu ID efakture kako bi se uzeli podaci
    def find_efakture_by_id(self, id_efakture):
        try:
            select_columns = "*"
            condition = 'idefakture'
            value = id_efakture
            connection = Database()
            pronadjene_efakture = connection.select_where(self.tablename, select_columns, condition, value)
            return pronadjene_efakture
        except Error as e:
            Greske("Pronalazenje u bazi efaktura pomocu ID - eFaktureController", e)