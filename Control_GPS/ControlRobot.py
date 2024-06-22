import time
import cv2
import Ultrasonico
import multiprocessing

import Object_Detection
import RPi.GPIO as GPIO
import YB_Pcb_Car
import DB_Controller
import datetime
import os


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
    def __init__(self):
        self.event = multiprocessing.Event()

        self.latitud = None
        self.longitud = None
        self.altitud = None
        self.tiempo = None

        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

        self.thread = None
        self.th_ia = None

        self.car = YB_Pcb_Car.YB_Pcb_Car()
        self.car.Car_Stop()
        self.lista = None
        self.db = DB_Controller.Database()

        buzzer = 32
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(buzzer, GPIO.OUT)  # Configura el pin del buzzer como salida
        self.Buzz = GPIO.PWM(buzzer, 440)  # Inicializa el PWM en el pin del buzzer con una frecuencia inicial de 440 Hz

    def avanzar_robot(self, x):
        if x == 0:
            print('no detecta')
        elif x < 106:
            print('izquierda')
            self.car.Car_Left(0, 50)
        elif x < 212:
            print('adelante')
            self.car.Car_Run(50, 50)
        else:
            print('derecha')
            self.car.Car_Right(50, 0)

    def ajustar_camara(self):
        self.car.Ctrl_Servo(1, 0)  # 0 = arriba, 80 = centro, 135 = abajo
        time.sleep(0.5)
        self.car.Ctrl_Servo(2, 0)  # 80 = frente, 0 = derecha, 180 = izquierda
        time.sleep(0.5)

    def iniciar_captura(self):
        self.ajustar_camara()
        time.sleep(2)
        print("Captura Iniciada")

        with multiprocessing.Manager() as manager:
            self.lista = manager.list([None, False])

            self.thread = multiprocessing.Process(target=self.mover_robot,
                                                  args=(self.lista, self.event,))
            self.th_ia = multiprocessing.Process(target=self.rutina_deteccion_ia,
                                                 args=(self.lista, self.event,))

            self.thread.start()
            self.th_ia.start()

            self.thread.join()
            self.th_ia.join()

    def mover_robot(self, lista, event):  # Gestiona el movimiento del robot
        lista[1] = True  # Indicando procesos de captura
        image = cv2.VideoCapture(0)
        setup_camara(image)
        self.ajustar_camara()
        while not event.is_set():
            ret, frame = image.read()
            if lista[1]:
                self.car.Car_Stop()
                time.sleep(5)
                lista[1] = False  # Habilita la detección nuevamente

            if ret:
                lista[0] = frame  # Almacenando imagen
            distance = Ultrasonico.Distance_test()

            if distance <= 40:
                event.set()  # Indicando detener captura y resto de procesos
                self.Buzz.start(50)
                Ultrasonico.play_buzzer(self.Buzz)
                self.Buzz.stop()
            else:
                self.avanzar_robot(200)

        time.sleep(1)
        self.car.Car_Stop()
        time.sleep(1)
        image.release()
        event.clear()
        print("Ciclo Finalizado")

    def rutina_deteccion_ia(self, lista, event):
        count = 0
        while not event.is_set():
            if lista[0] is not None and not lista[1]:
                resultado = Object_Detection.detectar(lista[0])
                if resultado is not None:
                    lista[1] = True  # Señala detener el movimiento
                    while not self.coordenadas_validas() and count < 5:
                        print("Obteniendo coordenadas")
                        count += 1
                    if count < 5:
                        now = datetime.datetime.now().strftime("%y%m%d%H%M%S")
                        name = f"{self.ROOT_DIR}/almacenamiento/imagen{now}.jpg"
                        success = cv2.imwrite(name, resultado)
                        if success:
                            print("Imagen guardada correctamente.")
                        else:
                            print("Error al guardar la imagen.")
                        self.db.insertar(self.latitud,
                                         self.longitud,
                                         self.altitud,
                                         self.tiempo,
                                         name)

    def detener_robot(self):
        self.event.set()  # Indicando detener captura y resto de procesos
        self.thread.join()
        self.th_ia.join()
        time.sleep(0.5)
        print("Robot detenido")

    def coordenadas(self, latitud, longitud, altitud, fecha):
        self.latitud = latitud
        self.longitud = longitud
        self.altitud = altitud
        self.tiempo = fecha
        '''if latitud != "******" and longitud != "******" and altitud != "******" and fecha != "******":
            self.latitud = latitud
            self.longitud = longitud
            self.altitud = altitud
            self.tiempo = fecha
        else:
            self.latitud = None
            self.longitud = None
            self.altitud = None
            self.tiempo = None'''

    def coordenadas_validas(self):
        if (self.latitud is not None and self.longitud is not None and self.altitud is not None
                and self.tiempo is not None):
            return True
        else:
            return False
        