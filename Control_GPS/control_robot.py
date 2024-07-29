import time
import cv2
# import ultrasonico
import multiprocessing
import object_detection

from threading import Thread
import RPi.GPIO as GPIO
import YB_Pcb_Car
import dbtiny_controller
import datetime
import os
import trazada
import trazada2

def setup_camara(image):
    image.set(3, 320)
    image.set(3, 320)
    image.set(4, 240)
    image.set(5, 30)  # set frame
    image.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    image.set(cv2.CAP_PROP_BRIGHTNESS, 62)
    image.set(cv2.CAP_PROP_CONTRAST, 63)
    image.set(cv2.CAP_PROP_EXPOSURE, 4800)

class ControlRobot:
    latitud = None
    longitud = None
    altitud = None
    tiempo = None
    thread = None
    th_ia = None
    lista = None
    coordenadas_objetivo = []

    def __init__(self):
        self.event = multiprocessing.Event()
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.car = YB_Pcb_Car.YB_Pcb_Car()
        self.trazada = trazada.Trazada()
        self.trazada2 = trazada2.Trazada()
        self.car.Car_Stop()
        self.db = dbtiny_controller.Database()
        self.pos = [16.75732, -93.17140]
        buzzer = 32
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(buzzer, GPIO.OUT)  # Configura el pin del buzzer como salida
        self.Buzz = GPIO.PWM(buzzer, 440)  # Inicializa el PWM en el pin del buzzer con una frecuencia inicial de 440 Hz

    def avanzar_robot(self, x):
        match x:
            case 0:
                print('no detecta')
                time.sleep(1)
                self.car.Car_Stop()
            case 100:
                print('izquierda')
                self.car.Car_Left(70,50)
                time.sleep(1)
                inicio = time.time()
                while time.time() - inicio < 0.5:
                    self.car.Car_Run(100, 100)
                time.sleep(1)
                self.car.Car_Stop()
            case 200:
                print('adelante')
                inicio = time.time()
                while time.time() - inicio < 0.5:
                    self.car.Car_Run(100, 100)
                time.sleep(1)
                self.car.Car_Stop()
            case 300:
                print('derecha')
                self.car.Car_Right(50, 70)
                time.sleep(1)
                inicio = time.time()
                while time.time() - inicio < 0.5:
                    self.car.Car_Run(100, 100)
                time.sleep(1)
                self.car.Car_Stop()
        
    def muestreo_coordenadas(self):
        tiempo_inicio = time.time()
        tiempo_espera = 5
        numero_lecturas = 5
        coordenadas = []
        while time.time() - tiempo_inicio < tiempo_espera:
            if self.altitud is not None and self.latitud is not None:
               coordenadas.append((float(self.latitud), float(self.longitud)))
            time.sleep(1)
        latitudes = [c[0] for c in coordenadas]
        longitudes = [c[1] for c in coordenadas]
        return (sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes))
                        
    def iniciar_captura(self):
        time.sleep(2)
        print("Captura Iniciada")
        self.thread = Thread(target = self.mover_robot)
        self.thread.daemon = True
        self.thread.start()
        
    def mover_robot(self):  # Gestiona el movimiento del robot
        print("iniciando...")
        image = cv2.VideoCapture(-1)
        if len(self.coordenadas_objetivo) != 0:
            self.trazada.trazada_basica(self.coordenadas_objetivo)
            print(f"numero de objetivos:")
            #self.trazada2.trazada_basica(self.coordenadas_objetivo)
            setup_camara(image)
            accion = 0
            while not self.event.is_set():
                ret, frame = image.read()
                if ret:
                    self.guardar_imagen(frame)
                    
                latitud, longitud = self.muestreo_coordenadas()
                accion = self.trazada.recorrido(latitud, longitud)
                #accion = self.trazada2.determinar_rumbo(latitud, longitud)
                if accion != -1:
                    self.avanzar_robot(accion)
                else:
                    break
        time.sleep(1)
        self.car.Car_Stop()
        time.sleep(1)
        image.release()
        self.event.clear()
        self.coordenadas_objetivo.clear()
        print("Ciclo Finalizado")
    
    def rutina_deteccion_ia(self, lista, event):
        count = 0
        while not event.is_set():
            if lista[0] is not None and not lista[1]:
                resultado = object_detection.detectar(lista[0])
                if resultado is not None:
                    lista[1] = True  # Señala detener el movimiento
                    while not self.pos_validas() and count < 5:
                        print("Obteniendo pos")
                        count += 1
                    if count < 5:
                        self.guardar_imagen(resultado)
        print("Detección IA detenida")

    def guardar_imagen(self, resultado):
        if self.pos_validas():
            now = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            name = f"imagen{now}.jpg"
            path = f"{self.ROOT_DIR}/almacenamiento"
            if cv2.imwrite(f"{path}/{name}", resultado):
                print("Imagen guardada correctamente.")
                self.db.insertar(self.latitud,
                                 self.longitud,
                                 self.altitud,
                                 self.tiempo,
                                 name,
                                 path,)
            else:
                print("Error al guardar la imagen.")

    def detener_robot(self):
        self.coordenadas_objetivo.clear()
        if self.thread is not None:
            self.event.set()  # Indicando detener captura y resto de procesos
            self.thread.join()
            time.sleep(0.5)
            print("Robot detenido")

    def set_coordenadas(self, latitud, longitud, altitud, fecha):
        self.latitud = latitud if latitud != "******" else None
        self.longitud = longitud if longitud != "******" else None
        self.altitud = altitud if altitud != "******" else None
        self.tiempo = fecha if fecha != "******" else None

    def pos_validas(self):
        return (self.latitud is not None
                and self.longitud is not None
                and self.altitud is not None
                and self.tiempo is not None)

    def set_elevacion(self, value):
        self.car.Ctrl_Servo(1, value)  # 0 = arriba, 80 = centro, 135 = abajo
        time.sleep(0.5)

    def set_rotacion(self, value):
        self.car.Ctrl_Servo(2, value)  # 80 = frente, 0 = derecha, 180 = izquierda
        time.sleep(0.5)

    def set_coord_objetivo(self, lat, long):
        self.coordenadas_objetivo.append((float(lat), float(long)))
                                    
