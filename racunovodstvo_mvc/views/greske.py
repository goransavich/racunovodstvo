from datetime import date

class Greske:

    def __init__(self, poruka, greska_sistem):
        # open the file using open() function
        file = open("poruka_greske.txt", 'a')
        today = date.today()
        datum = today.strftime("%d.%m.%Y.")
        poruka_greske = poruka+", " + str(greska_sistem) + " ," + datum
        # Add content in the file
        file.write(poruka_greske + '\n')

        # closing the file
        file.close()