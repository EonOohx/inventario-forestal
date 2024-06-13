import cv2
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread 
import cv2
import HSV_Config
import time
import YB_Pcb_Car  #Import Yahboom car library

class Interfaz:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Captura de imagenes desde la camara")
        
        global car
        car = YB_Pcb_Car.YB_Pcb_Car()
        # Inicializar la camara
        self.image = cv2.VideoCapture(0)

        self.image.set(3, 320)
        self.image.set(4, 240)
        self.image.set(5, 30)  #set frame
        self.image.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.image.set(cv2.CAP_PROP_BRIGHTNESS, 62) 
        self.image.set(cv2.CAP_PROP_CONTRAST, 63)
        self.image.set(cv2.CAP_PROP_EXPOSURE, 4800) 
        self.update_hsv = HSV_Config.update_hsv()
        
        self.color_hsv  = {"black"   : ((0, 0, 0), (80, 80, 80))}#,
                          #"green" : ((54, 109, 78), (77, 255, 255)),
                          #"blue"  : ((92, 100, 62), (121, 251, 255)),
                          #"yellow": ((26, 100, 91), (32, 255, 255))}
        
        # Variable para verificar si se esta capturando o no
        self.capturando = False
        
        # Boton para iniciar la captura
        self.boton_iniciar = tk.Button(ventana, text="Iniciar Captura", command=self.iniciar_captura)
        self.boton_iniciar.pack()
        
        # Boton para detener la captura
        self.boton_detener = tk.Button(ventana, text="Detener Captura", command=self.detener_captura)
        self.boton_detener.pack()
        
        # Mostrar la imagen en un widget Label
        self.label_imagen = tk.Label(ventana)
        self.label_imagen.pack()
        
    def iniciar_captura(self):
        self.capturando = True
        self.thread = Thread(target=self.mostrar_imagenes)
        self.thread.daemon = True
        self.thread.start()
    
    def detener_captura(self):
        global car
        time.sleep(0.5)
        car.Car_Stop() 
        self.capturando = False
    
    def mostrar_imagenes(self):
        global car
        inicial = time.time()
        final = inicial + 10
        car.Ctrl_Servo(1, 135) #  0 = arriba, 90 = frente, 135 = abajo
        time.sleep(0.5)
        car.Ctrl_Servo(2, 90) # 90 = frente, 0 = derecha, 180 = izquierda
        time.sleep(0.5)
        while time.time()<final:
            ret, frame = self.image.read()
            frame, binary, x, y = self.update_hsv.get_contours(frame,self.color_hsv)
            if ret: # MUESTRA LA IMAGEN EN LA INTERFAZ
                # Convertir la imagen a formato RGB
                #imagen_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convertir la imagen a formato de imagen de Tkinter
                imagen_tk = ImageTk.PhotoImage(Image.fromarray(frame))
                # Actualizar la imagen en la interfaz
                self.label_imagen.config(image=imagen_tk)
                self.label_imagen.image = imagen_tk
            #cv2.imshow('RGB',frame)
            print(x,y)
            if x==0:
                print('no detecta')
            elif x<106:
                print('izquierda')
                car.Car_Left(0, 50)
            elif x<212:
                print('adelante')
                car.Car_Run(40, 40)
            else:
                print('derecha')
                car.Car_Right(50, 0)
        time.sleep(0.5)
        car.Car_Stop()
        time.sleep(0.5)
        car.Ctrl_Servo(1, 90) #  0 = arriba, 90 = frente, 135 = abajo
        time.sleep(0.5)
        car.Ctrl_Servo(2, 0) # 90 = frente, 0 = derecha, 180 = izquierda
        time.sleep(0.5)
        
                
    def cerrar_ventana(self):
        self.ventana.quit()
        self.ventana.destroy()

# Crear la ventana principal
ventana = tk.Tk()

# Crear la instancia de la interfaz
interfaz = Interfaz(ventana)

# Configurar el cierre de la ventana
ventana.protocol("WM_DELETE_WINDOW", interfaz.cerrar_ventana)

# Ejecutar el bucle principal de la ventana
ventana.mainloop()

# Liberar la camara
interfaz.image.release()



