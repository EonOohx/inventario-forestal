import time
import numpy as np
import cv2
from threading import Thread
from PIL import ImageTk, Image
#import keyboard

import DeteccionPlanta
import Object_Detection
import ReconocerCamino
import HSV_Config
import YB_Pcb_Car


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
    capturas = 0
    proceso = False
    capturando = False
    h = 0
    s = 0
    v = 0
    imgBGR = np.array([0, 0], np.uint8)
    imgCV = np.array([0, 0], np.uint8)

    def __init__(self, *args):
        self.event = None
        self.detener = False
        self.action_image = None
        self.thread = None
        self.imgBGR = None
        self.imgCV = None
        self.es_bifurcacion = None
        self.x = None
        self.giro = 0

        self.car = YB_Pcb_Car.YB_Pcb_Car()
        self.car.Car_Stop()

        self.update_hsv = HSV_Config.update_hsv()
        self.color_hsv = {"black": ((0, 0, 0), (80, 80, 80))}

        self.label_imagen = args[0]
        self.boton_iniciar = args[1]
        self.boton_detener = args[2]
        self.boton_derecha = args[3]
        self.boton_izquierda = args[4]

    def apuntar_objetivo(self):
        self.car.Car_Stop()
        time.sleep(1)
        self.car.Ctrl_Servo(1, 80)  # 0 = arriba, 80 = centro, 135 = abajo
        if self.giro == 0:
            self.car.Ctrl_Servo(2, 0)  # 80 = frente, 0 = derecha, 180 = izquierda
        else:
            self.car.Ctrl_Servo(2, 180)  # 80 = frente, 0 = derecha, 180 = izquierda
        time.sleep(1)

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
        self.car.Ctrl_Servo(1, 125)  # 0 = arriba, 80 = centro, 135 = abajo
        time.sleep(0.5)
        self.car.Ctrl_Servo(2, 80)  # 80 = frente, 0 = derecha, 180 = izquierda
        time.sleep(0.5)

    def iniciar_captura(self):
        self.ajustar_camara()
        time.sleep(2)
        print("Captura Iniciada")
        self.thread = Thread(target=self.mover_robot)
        self.thread.daemon = True
        self.thread.start()
        self.boton_iniciar["state"] = "disabled"
        self.boton_derecha["state"] = "disabled"
        self.boton_izquierda["state"] = "active"
        self.boton_detener["state"] = "active"

    def prueba_imagen(self):
        image = cv2.VideoCapture(0)
        setup_camara(image)
        ret, frame = image.read()
        bgr = frame
        frame, binary, x, y = self.update_hsv.get_contours(frame, self.color_hsv)
        if ret:
            self.colocar_imagen(frame)
            self.imgBGR = frame
            cv2.imwrite("Imagen.jpg", bgr)
            # Parametros color = H, S, V, GIRO
            self.es_bifurcacion = ReconocerCamino.detectar_color(bgr, [0, 161, 255, 0])
            self.rutina_deteccion()
        image.release()
        print("Ciclo Finalizado")
        
    def mover_robot(self):  # Gestiona el movimiento del robot
        self.proceso = False
        self.capturando = True
        self.es_bifurcacion = None
        self.detener = False
        image = cv2.VideoCapture(0)
        setup_camara(image)
        while self.capturando:
            ret, frame = image.read()
            self.imgBGR = frame
            if ret:
                frame, binary, x, y = self.update_hsv.get_contours(frame[:100, :], self.color_hsv)
                self.colocar_imagen(frame)
                self.es_bifurcacion = ReconocerCamino.detectar_color(self.imgBGR, [0, 161, 255, 0])
            #time.sleep(1)
            if self.es_bifurcacion:
                self.apuntar_objetivo()
                image.release()
                image = cv2.VideoCapture(0)
                time.sleep(1)
                print("Detenerse")
                ret, frame = image.read()
                if ret:
                    self.imgBGR = frame
                    self.colocar_imagen(frame)
                    self.rutina_deteccion()
                    # self.rutina_deteccion_ia()
            else:
                self.avanzar_robot(x)
                
        time.sleep(1)
        self.car.Car_Stop()
        time.sleep(1)
        image.release()
        self.boton_iniciar["state"] = "active"
        self.boton_derecha["state"] = "disabled"
        self.boton_izquierda["state"] = "disabled"
        print("Ciclo Finalizado")    

    def rutina_avanzar(self):
        frame, binary, x, y = self.update_hsv.get_contours(self.imgBGR, self.color_hsv)
        self.x = x
        self.colocar_imagen(frame)
        self.es_bifurcacion = ReconocerCamino.detectar_color(self.imgBGR, [0, 161, 255, 0])

    def rutina_deteccion_ia(self):
        #Object_Detection.detectar(self.imgBGR)
        self.colocar_imagen(Object_Detection.detectar(self.imgBGR))
        time.sleep(10)
        inicio = time.time()
        time_final = inicio + 2
        self.colocar_imagen(cv2.imread("ITTG.png"))
        self.ajustar_camara()
        while time.time() < time_final and not self.detener:
            self.avanzar_robot(211)
        time.sleep(1)
    
    def rutina_deteccion(self):
        self.proceso = True
        self.imgCV = cv2.cvtColor(self.imgBGR, cv2.COLOR_BGR2HSV)
        self.action_image = self.label_imagen.bind("<Button-1>", self.muestreo)
        while self.proceso and not self.detener:
            pass
        inicio = time.time()
        time_final = inicio + 3
        self.ajustar_camara()
        self.colocar_imagen(cv2.imread("ITTG.png"))
        while time.time() < time_final and not self.detener:
            self.avanzar_robot(211)
        time.sleep(1)

    def detener_robot(self):
        self.capturando = False
        self.detener = True
        time.sleep(0.5)
        print(self.action_image)
        if self.action_image:
            self.label_imagen.unbind("<Button-1>", self.action_image)
        self.boton_detener["state"] = "disabled"
        print("Robot detenido")

    def colocar_imagen(self, imagen):
        imagen_tk = ImageTk.PhotoImage(Image.fromarray(imagen))
        self.label_imagen.config(image=imagen_tk)
        self.label_imagen.image = imagen_tk

    def girar_derecha(self):
        self.giro = 0
        self.boton_derecha["state"] = "disabled"
        self.boton_izquierda["state"] = "active"

    def girar_izquierda(self):
        self.giro = 1
        self.boton_derecha["state"] = "active"
        self.boton_izquierda["state"] = "disabled"

    def muestreo(self, event):  # Detecta los clicks en la imagen además de inciar el procesamiento de la imagen
        self.capturas += 1
        print(self.imgCV[event.y, event.x])
        punto_h, punto_s, punto_v = self.imgCV[event.y, event.x]
        self.h += punto_h
        self.s += punto_s
        self.v += punto_v
        if self.capturas == 5:
            print(f"{self.h / self.capturas} {self.s / self.capturas} {self.v / self.capturas}")
            image = DeteccionPlanta.calculo_hsv(self.h / self.capturas, self.s / self.capturas, self.v / self.capturas,
                                                self.imgBGR,
                                                self.imgCV)
            self.colocar_imagen(image)
            self.label_imagen.unbind("<Button-1>", self.action_image)
            self.action_image = None
            self.capturas = 0
            self.h = 0
            self.s = 0
            self.v = 0
            self.proceso = False
