from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske
# Connect to database


class GodinaConnection:
    tablename = "godina"

    def read(self):
        try:
            connection = Database()
            select_columns = "*"
            order = "naziv DESC"
            sve_godine = connection.select(self.tablename, select_columns, order)
            return sve_godine
        except Error as e:
            Greske("Greska trazenje godine u bazi podataka - GodinaController", e)

    def check_godina(self, uneta_godina):
        try:
            connection = Database()
            condition = 'naziv'
            value = uneta_godina
            sve_godine = connection.select_exists(self.tablename, condition, value)
            return sve_godine
        except Error as e:
            Greske("Greska trazenje da li postoji godina u bazi podataka - GodinaController", e)

    def insert_godina(self, godina):
        try:
            schema = "naziv"
            value = (godina,)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska unos godine - GodinaController", e)

    '''
    def insert(self, trenutna_godina):
        try:
            connection = Database()
            value = (trenutna_godina,)
            schema = "naziv"
            unesi_godinu = connection.insert(self.tablename, schema, value)
            return unesi_godinu
        except Error as e:
            Greske("Greska unos nove godine u bazu - GodinaController", e)
    '''