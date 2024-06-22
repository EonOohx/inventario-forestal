from tinydb import TinyDB, Query


class Database:
    
    def __init__(self):
        self.db = TinyDB('db.json')

    def insertar(self, latitud, longitud, altitud, tiempo, img_ref):
        return self.db.insert({'latitud':latitud,
                   'longitud':longitud, 'altitud':altitud, 'tiempo':tiempo,
                   'imgref':img_ref})
        
        
    def leer_todo(self):
        return self.db.all()


    def vaciar_todo(self):
        self.db.truncate()
    