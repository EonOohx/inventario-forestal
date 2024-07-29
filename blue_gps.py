import socket
import time

import serial
import control_robot
from threading import Thread
import RPi.GPIO as GPIO
import json


class Bluegpscliente:

    def __init__(self):
        self.maestro_thread = None
        self.adapter_address = 'F4:6A:DD:51:C4:64'
        port = 5  # Normal port for rfcomm?
        self.buf_size = 1024
        self.open_client = False
        self.estatus_conexion = -1
        print('Esperando conexión...')
        self.cliente = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.cliente.connect((self.adapter_address, port))
        print('conectado')
        self.serial_gps = serial.Serial()
        # self.cliente = socket.socket()
        self.gps_thread = None
        self.control_robot = control_robot.ControlRobot()
        self.abrir_comunicaciones()

    def abrir_comunicaciones(self):
        self.serial_gps = serial.Serial("/dev/ttyACM0", 9600)
        self.open_client = True
        self.cliente.send("Conectado".encode('utf-8'))
        self.estatus_conexion = 0
        
        self.gps_thread = Thread(target=self.leer_gps)
        self.gps_thread.daemon = True
        self.gps_thread.start()
        self.server_thread = Thread(target=self.leer_maestro)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.gps_thread.join()
        self.server_thread.join()
        GPIO.cleanup()

    def leer_gps(self):
        while self.open_client:
            data = (self.serial_gps.readline())  # read NMEA string received
            if data:
                data = data.decode('utf-8').replace("\r\n", "")
                # print(data)
                if data != "Iniciado" and data != "":
                    self.copia_datos(data)
                    self.cliente.send(data.encode('utf-8'))
                    
    def copia_datos(self, data):
        try:
            res = json.loads(data)
            #print(res)
            self.control_robot.set_coordenadas(res.get("latitud"),
                                           res.get("longitud"),
                                           res.get("altitud"),
                                           res.get("tiempo"), )
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")

    '''def restablecer_conexion(self):
        while True:
            if self.cliente.connect_ex(self.adapter_address) == 0:
                print("Conexión establecida")
                self.estatus_conexion = 0
                self.encendido_gps()
                break
            else:
                print("Reconectando...")
                time.sleep(1)'''

    def leer_maestro(self):
        try:
            while True:
                data_cliente = self.cliente.recv(self.buf_size)
                if data_cliente:
                    data_cliente = data_cliente.decode('utf-8')
                    print(data_cliente)
                    if "C" in data_cliente:
                        data = data_cliente.split()
                        self.control_robot.set_coord_objetivo(data[1], data[2])
                    match data_cliente:
                        case "1":
                            self.control_robot.iniciar_captura()
                        case "0":
                            self.control_robot.detener_robot()
                        case "U":
                            self.control_robot.set_elevacion(23)
                        case "J":
                            self.control_robot.set_elevacion(80)
                        case "M":
                            self.control_robot.set_elevacion(135)
                        case "I":
                            self.control_robot.set_rotacion(180)
                        case "O":
                            self.control_robot.set_rotacion(80)
                        case "P":
                            self.control_robot.set_rotacion(0)
        except ConnectionResetError:
            self.open_client = False
            
Bluegpscliente()
