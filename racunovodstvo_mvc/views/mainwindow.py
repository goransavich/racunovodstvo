
# Glavni prozor
class MainWindow:

    def __init__(self, master):
        self.master = master
        self.screen_width = str(master.winfo_screenwidth())
        self.screen_height = str(master.winfo_screenheight()-60)
        self.master.geometry(self.screen_width+'x'+self.screen_height+'+0+0')
        self.master.resizable(False, False)
        self.master.title("Finansijsko knjigovodstvo")
