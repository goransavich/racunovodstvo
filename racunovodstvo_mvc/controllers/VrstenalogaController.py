from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske
# Connect to database

class VrstenalogaController():

    tablename = "vrste_naloga"

    def read(self):
        try:
            connection = Database()
            select_columns = "*"
            svi_nalozi = connection.select(self.tablename, select_columns)
            return svi_nalozi
        except Error as e:
            Greske("Greska citanje svih vrsta naloga - VrstenalogaController",e)


    def update_nalog(self, naziv, id):
        # Ažuriranje baze podataka
        try:
            set_condition = 'vrste_naloga="{}"'.format(naziv)
            filter_condition = ' idvrste_naloga='+id
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Problem prilikom izmena vrste naloga - VrstenalogaController", e)


    def insert_nalog(self, naziv):
        try:
            schema = "vrste_naloga"
            value = (naziv,)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Problem unosa vrste naloga - VrstenalogaController", e)

    def delete_nalog(self, id):
        # Brisanje iz baze podataka
        try:
            delete_condition = "idvrste_naloga="+id
            connection = Database()
            connection.delete(self.tablename, delete_condition)
        except Error as e:
            Greske("Hmmmm, neka greška prilikom brisanja podataka vrste naloga - VrstenalogaController!", e)

