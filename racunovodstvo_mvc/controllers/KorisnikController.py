from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske


class KorisnikController:

    tablename = "korisnik"

    def find(self, id_korisnika):
        try:
            select_columns = "*"
            condition = 'idkorisnik'
            value = id_korisnika
            connection = Database()
            pronadjen_korisnik = connection.select_where(self.tablename, select_columns, condition, value)
            return pronadjen_korisnik
        except Error as e:
            Greske("Greska prilikom trazenja organizacije po sifri - KorisnikController", e)

    def izmeni_podatke(self, ime, naziv, jbkjs, program, projekat, funkcionalna, valuta):
        # Ažuriranje baze podataka
        try:
            set_condition = 'ime="{}"'.format(ime) + ', kompanija="{}"'.format(naziv) + ', jbkjs="{}"'.format(
                jbkjs) + ', program="{}"'.format(program) + ', projekat="{}"'.format(projekat) + ', funkcionalna="{}"'.format(
                funkcionalna) + ', valuta="{}"'.format(valuta)
            filter_condition = 'idkorisnik=1'
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska prilikom azuriranje podataka o organizaciji - KorisnikController.izmeni_podatke", e)

    def unesi_podatke(self, ime, naziv, jbkjs, program, projekat, funkcionalna, valuta):
        # Ažuriranje baze podataka
        try:
            schema = "ime, kompanija, jbkjs, program, projekat, funkcionalna, valuta"
            value = (ime, naziv, jbkjs, program, projekat, funkcionalna, valuta)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom unosa podataka o organizaciji - KorisnikController.unesi_podatke", e)
