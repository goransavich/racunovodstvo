from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske

class AplikacijaController():

    tablename = "aplikacija"

    def insert_aplikacija(self, sifra):
        try:
            schema = "sifra"
            value = (sifra,)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom unosa sifre aplikacije - AplikacijaController", e)


    def find(self):
        try:
            select_columns = "*"
            condition = 'idaplikacija'
            value = int(1)
            connection = Database()
            pronadjen_korisnik = connection.select_where(self.tablename, select_columns, condition, value)
            return pronadjen_korisnik
        except Error as e:
            Greske("Greska prilikom trazenja aplikacije po sifri - AplikacijaController", e)
