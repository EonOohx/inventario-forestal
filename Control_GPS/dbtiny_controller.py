from tinydb import TinyDB


class Database:
    
    def __init__(self):
        self.db = TinyDB('db.json')
        self.trecord_table = self.db.table("temp_records")
        self.tiffs_table = self.db.table("tiff_records")

    def insertar(self, latitud, longitud, altitud, tiempo, img_ref, table):
        return self.trecord_table.insert({'latitud':latitud,
                   'longitud':longitud, 'altitud':altitud, 'tiempo':tiempo,
                   'imgref':img_ref})
    
    def insertar_tiffs(self, tiffs:[]):...
        
    
    def leer_todo(self):
        return self.trecord_table.all()

    def vaciar_todo(self):
        self.trecord_table.truncate()
        
