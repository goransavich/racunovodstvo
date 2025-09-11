from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske

class OrisController:
    tablename = "oris"

    def unesi(self, id_naloga, broj_orisa):
        # Unos formiranog orisa u tabelu
        try:
            schema = "nalog_id, broj_oris"
            value = (id_naloga, broj_orisa)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska prilikom unosa podataka o oris - OrisController.unesi", e)

    def formiran_nalog_oris(self, id_naloga):
        try:
            where_columns = "nalog_id"
            value = id_naloga
            connection = Database()
            rezultat = connection.select_exists_where(self.tablename, where_columns, value)
            return rezultat[0][0]
        except Error as e:
            Greske("Hmmmm, neka greška prilikom povezivanja na bazu podataka! provera da li je formiran ORIS od trazenog naloga - OrisController.formiran_nalog_oris", e)

    # Ovde se proverava da li postoji broj oris dokumenta u tabeli (na jedan dan moze da bude vise istih brojeva koji se razlikuju po poslednjoj cifri)
    def postoji_broj_u_orisu(self, broj):
        try:
            select_columns = "*"
            where_columns = "LEFT (broj_oris, 10)"
            value = broj
            connection = Database()
            pronadjen_nalog = connection.select_where(self.tablename, select_columns, where_columns, value)
            return pronadjen_nalog
        except Error as e:
            Greske("Pronalazenje u bazi naloga pomocu broja orisa - OrisController.postoji_broj_u_orisu ", e)
