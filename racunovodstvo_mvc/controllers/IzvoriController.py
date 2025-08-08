from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske

# Connect to database

class IzvoriController():
    tablename = "izvori_finansiranja"

    def read(self):
        try:
            connection = Database()
            select_columns = "*"
            order = 'sifra'
            svi_izvori = connection.select(self.tablename, select_columns, order)
            return svi_izvori
        except Error as e:
            Greske("Greska, citanje svih izvora finansiranja iz baze - IzvoriController", e)


    def update_izvor(self, sifra, naziv, id):
        # Ažuriranje baze podataka
        try:
            connection = Database()
            set_condition = 'sifra="{}"'.format(sifra)+', naziv="{}"'.format(naziv)
            filter_condition = ' idizvori_finansiranja='+id
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska, update izvora finansiranja  - IzvoriController", e)


    def insert_izvor(self, sifra, naziv):
        try:
            connection = Database()
            schema = "sifra, naziv"
            value = (sifra, naziv)
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska, unos novog izvora finansiranja  - IzvoriController", e)


    def delete_izvor(self, id):
        # Brisanje iz baze podataka
        try:
            connection = Database()
            delete_condition = "idizvori_finansiranja="+id
            connection.delete(self.tablename, delete_condition)
        except Error as e:
            Greske("Greska, brisanje izvora finansiranja  - IzvoriController", e)

    def find(self, oznaka_izvora):
        try:
            select_columns = "*"
            condition = 'sifra'
            value = oznaka_izvora
            connection = Database()
            sve_konto = connection.select_where(self.tablename, select_columns, condition, value)
            return sve_konto
        except Error as e:
            Greske("Greska, pronalazenje po oznaci  - IzvoriController", e)

    def pronadji_oznaku_po_sifri(self, sifra_izvora):
        try:
            select_columns = "sifra"
            condition = 'idizvori_finansiranja'
            value = sifra_izvora
            connection = Database()
            sve_oznake = connection.select_where(self.tablename, select_columns, condition, value)
            return sve_oznake
        except Error as e:
            Greske("Greska, pronalazenje po sifri  - IzvoriController", e)