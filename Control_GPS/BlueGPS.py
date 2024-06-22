import socket
import serial
import ControlRobot
from threading import Thread
import RPi.GPIO as GPIO
import json

class BluegpsServer:

    def __init__(self):
        adapter_address = 'AA:AA:AA:AA:AA:AA'
        port = 4  # Normal port for rfcomm?
        self.buf_size = 1024
        self.open_client = False
        self.estatus_conexion = -1

        self.server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.server.bind((adapter_address, port))
        self.server.listen(1)
        self.serial_gps = serial.Serial()
        self.client = socket.socket()
        
        self.gps_thread = None

        self.control_Robot = ControlRobot.ControlRobot()

        self.abrir_comunicaciones()


    def abrir_comunicaciones(self):
        try:
            print('Listening for connection...')
            self.client, address = self.server.accept()
            self.open_client = True
            print(f"Connected to {address}")
            self.serial_gps = serial.Serial("/dev/ttyACM0", 9600)

            self.client.send("Conectado".encode('utf-8'))
            
            self.estatus_conexion = 0
            
            self.gps_thread = Thread(target=self.leer_gps)
            self.gps_thread.daemon = True
            self.gps_thread.start()
            
            while True:
                if self.estatus_conexion == -1:
                    self.restablecer_conexion()
                self.leer_maestro()
        except Exception as e:
            print(f'Something went wrong: {e}')
        finally:
            self.open_client = False
            self.client.close()
            self.server.close()
            print("Medición detenida por el usuario")
            GPIO.cleanup()


    def leer_gps(self):
        try:
            while True:
                data = (self.serial_gps.readline())  # read NMEA string received
                if data and self.open_client:
                    data = data.decode('utf-8').replace("\r\n", "")
                    print(data)
                    if data != "Iniciado" and data is not None and data != "":
                        try:
                            res = json.loads(data)
                            print(res.get("latitud"))
                            #print(res)
                            self.control_Robot.coordenadas(res.get("latitud"),
                                                           res.get("longitud"),
                                                           res.get("altitud"),
                                                           res.get("tiempo"),
                                                          )
                            self.client.send(data.encode('utf-8'))
                        except json.JSONDecodeError as e:
                            print(f"Error al decodificar JSON: {e}")
        except ConnectionAbortedError as e:
            self.estatus_conexion = -1
            
        
    def restablecer_conexion(self):
        while True:
            if self.server.connect_ex(adapter_address) == 0:
                print("Conexión establecida")
                self.estatus_conexion = 0
                self.encendido_gps()
                break
            else:
                print("Reconectando...")
                time.sleep(1)
                

    def leer_maestro(self):
        data_cliente = self.client.recv(self.buf_size)
        if data_cliente:
            data_cliente = data_cliente.decode('utf-8')
            print(data_cliente)
            if data_cliente == "1":
                self.control_Robot.iniciar_captura()
            elif data_cliente == "0":
                self.control_Robot.detener_robot()

    
    
BluegpsServer()
