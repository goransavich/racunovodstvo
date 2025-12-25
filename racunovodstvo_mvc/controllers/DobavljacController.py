from mysql.connector import Error
from racunovodstvo_mvc.controllers.connections import Database
from racunovodstvo_mvc.views.greske import Greske

# Connect to database
class DobavljacController:

    tablename = "dobavljaci"

    def read(self):
        try:
            select_columns = "*"
            order = 'naziv'
            connection = Database()
            svi_dobavljaci = connection.select(self.tablename, select_columns, order)
            return svi_dobavljaci
        except Error as e:
            Greske("Greska citanje svih dobavljaca - DobavljaciController", e)

    def pronadji_dobavljaca(self, pib):
        try:
            condition = 'pib'
            connection = Database()
            postoji = connection.select_exists(self.tablename, condition, pib)
            return postoji
        except Error as e:
            Greske("Greska pronadji dobavljaca - DobavljaciController", e)

    def pronadji_dobavljaca_svi_podaci(self, pib):
        try:
            condition = 'pib'
            select_columns = "*"
            connection = Database()
            pronadjen = connection.select_where(self.tablename, select_columns, condition, pib)
            return pronadjen
        except Error as e:
            Greske("Greska pronadji dobavljaca svi podaci - DobavljaciController", e)

    def pronadji_dobavljaca_po_id_konta(self, kontoid):
        try:
            condition = 'id_konta'
            select_columns = "*"
            connection = Database()
            pronadjen = connection.select_where(self.tablename, select_columns, condition, kontoid)
            return pronadjen
        except Error as e:
            Greske("Greska pronadji dobavljaca svi podaci - DobavljaciController", e)

    def unos_dobavljaca_u_tabelu(self, pib, naziv, idkonta, mesto, adresa):
        try:
            schema = "naziv, pib, id_konta, mesto, adresa"
            value = (naziv, pib, idkonta, mesto, adresa)
            connection = Database()
            connection.insert(self.tablename, schema, value)
        except Error as e:
            Greske("Greska unos dobavljaca u tabelu dobavljaci - DobavljacController", e)

    def update_dobavljaca(self, naziv, id_dobavljaca, mesto, adresa):
        # Ažuriranje baze podataka
        try:
            set_condition = 'naziv="{}"'.format(naziv) + ', mesto="{}"'.format(mesto) + ', adresa="{}"'.format(adresa)
            filter_condition = ' iddobavljaci=' + id_dobavljaca
            connection = Database()
            connection.update(self.tablename, set_condition, filter_condition)
        except Error as e:
            Greske("Greska prilikom azuriranje dobavljaca - DobavljacController", e)

    # Brisanje iz baze podataka
    def delete_dobavljaca(self, dobavljac_id):
        try:
            delete_condition = "iddobavljaci=" + dobavljac_id
            connection = Database()
            connection.delete(self.tablename, delete_condition)
        except Error as e:
            Greske("Greska brisanje dobavljaca - DobavljacController", e)

