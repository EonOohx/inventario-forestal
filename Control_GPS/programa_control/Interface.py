import tkinter as tk
from tkinter import ttk
import bluegps_server
import observable as observer
from threading import Thread


class Interface:
    estado = "Apagado"
    entry_lat = None
    entry_long = None
    bg_client = None
    ROW_CONEXION = 1
    ROW_COORDENADAS = 3
    ROW_MOVCONTROL = 6
    ROW_MOVCAMARA = 8

    def __init__(self):
        self.observable = observer.ObservableBool(False)
        hilo = Thread(target=self.iniciar_conexion)
        hilo.daemon = True
        hilo.start()

        self.root = tk.Tk()
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.cargar_elementos()

        self.root.mainloop()

    def iniciar_conexion(self):
        self.bg_client = bluegps_server.BluegpsServer(self.observable)

    def cargar_elementos(self):
        self.root.title("Control Robot")
        self.frm = tk.Frame(self.root, padx=10, pady=10)
        self.frm.grid(row=0, column=0, sticky="ew")

        tk.Label(self.frm, text="Control de Movimiento", font=("Arial", 16)).grid(column=1, row=self.ROW_MOVCONTROL - 1)

        # Configurar la expansión de las columnas para que ocupen el mismo espacio
        self.frm.grid_columnconfigure(0, weight=1)
        self.frm.grid_columnconfigure(1, weight=1)
        self.frm.grid_columnconfigure(2, weight=1)
        self.frm.grid_columnconfigure(3, weight=1)

        self.seccion_conexion()
        self.seccion_coordenadas()
        self.seccion_movimiento()
        self.seccion_camara()

    def seccion_conexion(self):
        # Control de conexión
        tk.Label(self.frm, text="Control de Conexión", font=("Arial", 16)).grid(column=1, row=self.ROW_CONEXION - 1)

        (tk.Button(self.frm, text="Cerrar Programa", command=lambda: self.cerrar(), width=20, height=2)
         .grid(column=2, row=self.ROW_CONEXION, padx=(5, 0), pady=5, sticky="ew"))

        buscar_btn = tk.Button(self.frm, text="Buscar/Apagar Conexión", command=self.bg_client.busqueda, width=20,
                               height=2)
        buscar_btn.grid(column=0, row=self.ROW_CONEXION, padx=(0, 5), pady=5, sticky="ew")

        estado_lb = tk.Label(self.frm, text=self.estado, bg="red")
        estado_lb.grid(column=1, row=self.ROW_CONEXION, padx=(5, 5), pady=5, sticky="ew")

        hilo = Thread(target=self.estado_busqueda, args=(estado_lb,))
        hilo.daemon = True
        hilo.start()

    def seccion_movimiento(self):
        # Botones de control de movimiento
        (tk.Button(self.frm, text="Arrancar", command=lambda: self.bg_client.enviar_mensaje("1"), width=20, height=2)
         .grid(column=0, row=self.ROW_MOVCONTROL, padx=(0, 5), pady=5, sticky="ew"))

        (tk.Button(self.frm, text="Detener", command=lambda: self.bg_client.enviar_mensaje("0"), width=20, height=2)
         .grid(column=1, row=self.ROW_MOVCONTROL, padx=(5, 0), pady=5, sticky="ew"))

    def seccion_coordenadas(self):
        # Ajuste de la cámara
        lat = tk.StringVar()
        long = tk.StringVar()
        tk.Label(self.frm, text="Coordenadas", font=("Arial", 16)).grid(column=1, row=self.ROW_COORDENADAS - 1)
        tk.Label(self.frm, text="Latitud", font=("Arial", 16)).grid(column=0, row=self.ROW_COORDENADAS)
        self.entry_lat = tk.Entry(self.frm, width=20, textvariable=lat)
        self.entry_lat.grid(column=1, row=self.ROW_COORDENADAS, padx=(0, 5), pady=5, sticky="ew")
        tk.Label(self.frm, text="Longitud", font=("Arial", 16)).grid(column=2, row=self.ROW_COORDENADAS)
        self.entry_long = tk.Entry(self.frm, width=20, textvariable=long)
        self.entry_long.grid(column=3, row=self.ROW_COORDENADAS, padx=(0, 5), pady=5, sticky="ew")
        (tk.Button(self.frm, text="Establecer", width=20, height=2,
                   command=lambda: self.enviar_coordenadas(lat.get(), long.get()))
         .grid(column=0, row=self.ROW_COORDENADAS + 1, padx=(5, 0), pady=5, sticky="ew"))

    def seccion_camara(self):
        # Ajuste de la cámara
        tk.Label(self.frm, text="Ajusta Cámara", font=("Arial", 16)).grid(column=1, row=self.ROW_MOVCAMARA - 1)

        (tk.Button(self.frm, text="Arriba", command=lambda: self.bg_client.enviar_mensaje("U"), width=20, height=2)
         .grid(column=0, row=self.ROW_MOVCAMARA, padx=(0, 5), pady=5, sticky="ew"))

        (tk.Button(self.frm, text="Al Centro", command=lambda: self.bg_client.enviar_mensaje("J"), width=20, height=2)
         .grid(column=1, row=self.ROW_MOVCAMARA, padx=(5, 5), pady=5, sticky="ew"))

        (tk.Button(self.frm, text="Abajo", command=lambda: self.bg_client.enviar_mensaje("M"), width=20, height=2)
         .grid(column=2, row=self.ROW_MOVCAMARA, padx=(5, 0), pady=5, sticky="ew"))

        tk.Button(self.frm, text="Izquierda", command=lambda: self.bg_client.enviar_mensaje("I"), width=20,
                  height=2).grid(column=0, row=self.ROW_MOVCAMARA + 1, padx=(0, 5), pady=5, sticky="ew")

        tk.Button(self.frm, text="En Frente", command=lambda: self.bg_client.enviar_mensaje("O"), width=20,
                  height=2).grid(column=1, row=self.ROW_MOVCAMARA + 1, padx=(5, 5), pady=5, sticky="ew")

        (tk.Button(self.frm, text="Derecha", command=lambda: self.bg_client.enviar_mensaje("P"), width=20, height=2)
         .grid(column=2, row=self.ROW_MOVCAMARA + 1, padx=(5, 0), pady=5, sticky="ew"))

    def estado_busqueda(self, label):
        while True:
            if self.observable.value:
                self.estado = "Encendido"
                label["background"] = "green"
            elif self.observable.value is False:
                self.estado = "Apagado"
                label["background"] = "red"
            label["text"] = self.estado

    def enviar_coordenadas(self, lat, long):
        self.entry_lat.delete(0, 'end')
        self.entry_long.delete(0, 'end')
        self.bg_client.enviar_mensaje(f"C {lat} {long}")

    def cerrar(self):
        self.bg_client.cerra_conexion()
        self.root.destroy()


Interface()
