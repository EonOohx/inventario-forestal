import tkinter as tk
import ControlRobot
from PIL import ImageTk, Image

def centrar(r):
    altura = 500
    anchura = 500
    altura_pantalla = r.winfo_screenheight()
    anchura_pantalla = r.winfo_screenwidth()
    x = (anchura_pantalla // 2) - (anchura // 2)
    y = (altura_pantalla // 2) - (altura // 2)
    r.geometry("+" + str(x) + "+" + str(y))

 
class Interface:

    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.ventana.title("RaspBot")

        # Mostrar la imagen en un widget Label
        imagen = ImageTk.PhotoImage(Image.open("/home/pi/Downloads/SeguidorLinea/ITTG.png"))
        self.label_imagen = tk.Label(self.ventana, image = imagen)
        self.label_imagen.image = imagen
        self.label_imagen.pack()

        contenedor_botones = tk.Frame(self.ventana, bg="blue")
        contenedor_botones.pack(padx=(50, 50), pady=(20, 0))
        tk.Label(contenedor_botones, text="Dirección de la cámara").pack()
    
        # Boton para iniciar la captura
        self.boton_iniciar = tk.Button(contenedor_botones, text="Iniciar Captura")
        self.boton_iniciar.pack(side="top")

        self.boton_izquierda = tk.Button(contenedor_botones, text="Izquierda")
        self.boton_izquierda.pack(side="left")

        self.boton_derecha = tk.Button(contenedor_botones, text="Derecha")
        self.boton_derecha.pack(side="right")

        # Boton para detener la captura
        self.boton_detener = tk.Button(self.ventana, text="Detener Captura", state="disabled")
        self.boton_detener.pack(pady=(0, 20))

        self.control_robot = ControlRobot.ControlRobot(self.label_imagen,
                                                       self.boton_iniciar,
                                                       self.boton_detener,
                                                       self.boton_derecha,
                                                       self.boton_izquierda)

        self.boton_iniciar.config(command=self.control_robot.iniciar_captura)

        self.boton_detener.config(command=self.control_robot.detener_robot)

        self.boton_derecha.config(command=self.control_robot.girar_derecha)

        self.boton_izquierda.config(command=self.control_robot.girar_izquierda)

        centrar(self.ventana)
        self.ventana.resizable(0, 0)
        self.ventana.mainloop()

    def cerrar_ventana(self):
        self.ventana.quit()
        self.ventana.destroy()


if __name__ == "__main__":
    Interface()
