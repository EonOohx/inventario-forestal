import math


def truncar(numero, decimales=5):
    factor = 10.0 ** decimales
    return math.trunc(numero * factor) / factor

def magnitud_vector(lat_f, long_f, lat_i = 0, long_i = 0):
    return math.sqrt(pow(lat_f - lat_i, 2) + pow(long_f - long_i, 2))

def angulo(lat_f, long_f):
    return math.degrees(math.atan((long_f) / (mag_actual * mag_objetivo)))

class Trazada:
    mov_latitudinal = False
    coords = []
    m_vectores = []
    list_angulos_objetivo = []
    
    
    def trazada_basica(self, coordenadas):
        self.coords.clear()
        self.coords = coordenadas
        self.m_vectores = list(map(lambda c : magnitud_vector(c[0], c[1]), self.coords))
        #math.degrees(math.acos(producto_escalar / (mag_actual * mag_objetivo)))
        print(len(self.m_vectores))
        print(len(self.coords))
    

        
        
    '''def recorrido(self, lat_actual, long_actual):
        if len(self.coords) == 0:
            return -1
        
        lat_actual = truncar(lat_actual, 6)
        long_actual = truncar(long_actual, 6)
        lat_objetivo, long_objetivo = self.coords[-1]
        
        print(f"Ruta actual: {self.coords[-1][0], self.coords[-1][1]}")
        print(f"poss actual: {lat_actual}, {long_actual}")
        print(f'magnitud actual: {magnitud_vector(lat_objetivo, long_objetivo, lat_actual, long_actual)}')
        
        if (long_objetivo - 0.000015 <= long_actual <= long_objetivo + 0.000015
            and lat_objetivo - 0.000015 <= lat_actual <= lat_objetivo + 0.000015):
            print(f"Ruta alcanzada: {self.coords[-1]}")
            self.coords.pop()
            self.m_vectores.pop()
            return 0
        
        angulo = self.rumbo_actual(lat_actual, long_actual, lat_objetivo, long_objetivo)
        print(f"angulo: {angulo}")
        if 0 <= angulo * 100000 <= 25:
            return 200
        else:
          if longitud_actual > longitud_objetivo:
               return 100
        else:
            return 300'''
        
    def rumbo_actual(self, lat_actual, long_actual, lat_objetivo, long_objetivo):
        lat_actual = 1 if lat_actual == 0 else lat_actual
        long_actual = 1 if long_actual == 0 else long_actual
        mag_actual = magnitud_vector(lat_actual, long_actual)
        print(f"magnitud punto: {mag_actual}")
        mag_objetivo = self.m_vectores[-1]
        print(f"magnitud objetivo: {mag_objetivo}")
        producto_escalar = lat_actual * lat_objetivo + long_actual * long_objetivo
        print(f"producto_escalar: {producto_escalar}")
        return (math.degrees(math.acos(producto_escalar / (mag_actual * mag_objetivo))))
                    

    def recorrido(self, lat_actual, long_actual):
        if len(self.coords) == 0:
            return -1
            
        long_actual = truncar(long_actual, 4)
        lat_actual = truncar(lat_actual, 4)
        latitud_objetivo, longitud_objetivo = self.coords[-1]

        print(f"Ruta actual: {self.coords[-1]}")
        print(f"poss actual: {lat_actual}, {long_actual}")
        var = 0.000015
        if (long_actual == longitud_objetivo
            and latitud_objetivo == lat_actual):
            print(f"Ruta alcanzada: {self.coords[-1]}")
            self.coords.pop()
            return 0
        var2 = 0.000001
        avance_latitudinal = math.sqrt(
            pow(longitud_objetivo - long_actual, 2)+ pow(latitud_objetivo - lat_actual + 0.00001, 2))
        avance_longitudinal_d = math.sqrt(pow(longitud_objetivo - long_actual + 0.00001, 2) +
                                          pow(latitud_objetivo - lat_actual, 2))
        avance_longitudinal_i = math.sqrt(pow(longitud_objetivo - long_actual - 0.00001, 2) +
                                          pow(latitud_objetivo - lat_actual, 2))
        
        print(f"avance derecha: {avance_longitudinal_d}")
        print(f"avance izquierda: {avance_longitudinal_i}")
        print(f"avance de frente: {avance_latitudinal}")
        if avance_longitudinal_d > avance_latitudinal or avance_longitudinal_i > avance_latitudinal:
            # se invierte los valores de longitud por los de latitud
            longitud_objetivo = latitud_objetivo
            long_actual = lat_actual
            if not self.mov_latitudinal:
                print("Comparado valores latitudinales")
                self.mov_latitudinal = True
                #return (300 if avance_longitudinal_d > avance_longitudinal_i else 100), False
        else:
            print("Comparado valores longitudinales")
            self.mov_latitudinal = False
            
        if long_actual == longitud_objetivo:
            return 200
        elif long_actual > longitud_objetivo:
           return 100
        elif long_actual < longitud_objetivo:
            return 300
    
    '''def recorrido(self):
        if len(self.coords) == 0:
            return -1
            
        long_actual = truncar(long_actual, 4)
        lat_actual = truncar(lat_actual, 4)
        lat_objetivo, long_objetivo = self.coords[-1]
        
        
        
    
    def calculos(self, long_actual, lat_actual, lat_objetivo, long_objetivo):
        delta_pi = lat_objetivo - lat_actual
        delta_lambda = long_objetivo - long_actual'''
        
        