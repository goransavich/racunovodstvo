from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske

class KreiranNalogController():
    tablename = "nalog"

    def insert_nalog(self, datum, broj, proknjizen, vrsta, korisnik):
        try:
            schema = "datum, broj, proknjizen, vrsta, korisnik"
            value = (str(datum), broj, proknjizen, vrsta, korisnik)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom formiranja novog naloga", e)

    def update_nalog(self, nalog_id, proknjizen, datum_knjizenja, korisnik):
        # Ažuriranje baze podataka
        try:
            set_condition = 'proknjizen="{}"'.format(proknjizen) + ', datum_knjizenja="{}"'.format(datum_knjizenja) + ', korisnik={}'.format(korisnik)
            filter_condition = ' nalogID={}'.format(nalog_id)
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska prilikom azuriranje stavke naloga", e)
