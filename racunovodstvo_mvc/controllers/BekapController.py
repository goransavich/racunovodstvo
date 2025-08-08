from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske


class BekapController:

    tablename = "bekap"

    def insert_bekap(self, datum):
        try:
            schema = "datum_bekapa"
            value = (datum,)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom unosa datuma bekapa - BekapController", e)

    def find_last(self):
        try:
            select_columns = "*"
            order = "datum_bekapa DESC"
            connection = Database()
            pronadjen_korisnik = connection.select(self.tablename, select_columns, order)
            return pronadjen_korisnik
        except Error as e:
            Greske("Greska prilikom trazenja aplikacije po sifri - AplikacijaController", e)
