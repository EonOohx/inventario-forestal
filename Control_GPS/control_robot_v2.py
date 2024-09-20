import time
import cv2
# import ultrasonico
import multiprocessing
import yolo_model_controller

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


'''def tiff(latitud, longitud, altitud, tiempo, nombre, ruta):
    with open(f"{nombre}/{ruta}") as img:   
        img = Image(img)
        img.gps_latitude = latitud
        img.gps_longitude = longitud
        img.gps_altitude = altitud
        img.datetime_original = tiempo'''


class ControlRobot:
    latitud = None
    longitud = None
    altitud = None
    tiempo = None
    thread = None
    thread_imagenes = None
    semaforo = None
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
        self.yolo = yolo_model_controller.YoloControl()
        
        #self.pos = [16.75732, -93.17140]
        buzzer = 32
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(buzzer, GPIO.OUT)  # Configura el pin del buzzer como salida
        self.Buzz = GPIO.PWM(buzzer, 440)  # Inicializa el PWM en el pin del buzzer con una frecuencia inicial de 440 Hz

    def avanzar_robot(self, x, fuerza_giro = 40):
        match x:
            case 0:
                print('no detecta')
                time.sleep(1)
                self.car.Car_Stop()
            case 100:
                print('izquierda')
                self.car.Car_Left(fuerza_giro,40)
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
                self.car.Car_Right(40, fuerza_giro)
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
        latitudes = 0
        longitudes = 0
        while time.time() - tiempo_inicio < tiempo_espera:
            if self.altitud is not None and self.latitud is not None:
                latitudes += float(self.latitud)
                longitudes += float(self.longitud)
            time.sleep(1)
        return (latitudes / numero_lecturas, longitudes / numero_lecturas)
                        
    def iniciar_captura(self):
        time.sleep(2)
        print("Captura Iniciada")
        #self.thread = Thread(target = self.mover_robot)
        #self.thread_imagenes = Thread(target = self.iniciar_captura)
        self.semaforo = multiprocessing.Value("i", 1)
        self.thread = multiprocessing.Process(target = self.mover_robot, args=(self.semaforo,))
        self.thread_imagenes = multiprocessing.Process(target = self.iniciar_imagenes, args=(self.semaforo,))       
        self.thread.daemon = True
        self.thread_imagenes.daemon = True
        self.thread_imagenes.start()
        self.thread.start()
  
        
    def mover_robot(self, semaforo):  # Gestiona el movimiento del robot
        print("iniciando...")
        #self.trazada.trazada_basica([(16.7575, -93.1715), (16.7575, -93.1713)])
        if len(self.coordenadas_objetivo) != 0:
            self.trazada.trazada_basica(self.coordenadas_objetivo)
            print(f"numero de objetivos: {self.coordenadas_objetivo}")
            #self.trazada2.trazada_basica(self.coordenadas_objetivo)
            accion = 0
            while semaforo.value == 1:   
                latitud, longitud = self.muestreo_coordenadas()
                accion, fuerza_giro = self.trazada.recorrido2(latitud, longitud)
                #accion = self.trazada2.determinar_rumbo(latitud, longitud)
                if accion != -1:
                    self.avanzar_robot(accion, fuerza_giro)
                else:
                    break
        self.semaforo.value = 0
        time.sleep(1)
        self.car.Car_Stop()
        time.sleep(1)
        self.event.clear()
        self.coordenadas_objetivo.clear()
        print("Ciclo Finalizado")

    def iniciar_imagenes(self, semaforo):
        image = cv2.VideoCapture(0)
        setup_camara(image)
        tiempo_inicial = time.time()
        while semaforo.value == 1:
            if time.time() - tiempo_inicial > 2:
                ret, frame = image.read()
                if ret:
                    self.guardar_imagen(frame)
                tiempo_inicial = time.time()
                time.sleep(1)
        image.release()
    
    def guardar_imagen(self, resultado):
        if self.pos_validas():
            now = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            name = f"imagen{now}.jpg"
            path = f"{self.ROOT_DIR}/almacenamiento"
            if cv2.imwrite(f"{path}/{name}", resultado):
                print("Imagen guardada correctamente.")
                cv2.imwrite(f"{self.ROOT_DIR}/detecciones/{name}",
                            self.yolo.detectar_objetos(resultado)
                            )
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
        self.semaforo.value = 0
        print("Robot detenido")
        self.thread.join()
        self.thread_imagenes.join()
#        if self.thread is not None:
#            self.event.set()  # Indicando detener captura y resto de procesos
#            self.thread.join()
#            time.sleep(0.5)
#            print("Robot detenido")

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
                                    
    '''def exportar_imagenes(self):
        datos = self.db.leer_todo()
        map(lambda record:tiff(record),datos)
        dbmongo_api.exportar_datos(datos)'''
