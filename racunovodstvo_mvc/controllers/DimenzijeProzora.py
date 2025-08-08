
class DimenzijeProzora:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    # Sirina prozora Dnevnik knjizenja i izvrsenja budzeta
    def odredi_sirinu_dnevnik_izvrsenje(self):
        if self.screen_width < 1400:
            return self.screen_width - 200
        else:
            return self.screen_width - 600

    # Visina prozora Dnevnik knjizenja
    def odredi_visinu_dnevnik(self):
        if self.screen_height < 800:
            return self.screen_height - 180
        else:
            return self.screen_height - 320

    # Visina prozora Izvrsenje budzeta
    def odredi_visinu_izvrsenje(self):
        if self.screen_height < 800:
            return self.screen_height - 200
        else:
            return self.screen_height - 420

    # Sirina prozora Kartica konta i Stanje konta
    def odredi_sirinu_kartica_konta_stanje(self):
        if self.screen_width < 1400:
            return self.screen_width - 300
        else:
            return self.screen_width - 800

    # Visina prozora Kartica konta i Stanje konta
    def odredi_visinu_kartica_konta_stanje(self):
        if self.screen_height < 800:
            return self.screen_height - 180
        else:
            return self.screen_height - 420

    # Sirina prozora Zakljucni list
    def odredi_sirinu_zakljucni_list(self):
        if self.screen_width < 1400:
            return self.screen_width - 120
        else:
            return self.screen_width - 400

    # Visina prozora Zakljucni list
    def odredi_visinu_zakljucni_list(self):
        if self.screen_height < 800:
            return self.screen_height - 140
        else:
            return self.screen_height - 400

    # Sirina prozora Kreiran nalog
    def odredi_sirinu_kreiran_nalog(self):
        if self.screen_width < 1400:
            return self.screen_width - 100
        else:
            return self.screen_width - 300

    # Visina prozora Kreiran nalog
    def odredi_visinu_kreiran_nalog(self):
        if self.screen_height < 800:
            return self.screen_height - 80
        else:
            return self.screen_height - 120

    # Sirina prozora GLAVNA KNJIGA
    def odredi_sirinu_glavna_knjiga(self):
        return 600

    # Visina prozora GLAVNA KNJIGA
    def odredi_visinu_glavna_knjiga(self):
        return 300
