import socket
from threading import Thread


class BluegpsServer:
    adapter_addr = 'XX:XX:XX:XX:XX:XX'
    port = 5  # Normal port for rfcomm?
    buf_size = 1024
    server = None
    cliente = None
    buscar = False
    hilo = None

    def __init__(self, observable):
        self.ob = observable

        self.server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.server.bind((self.adapter_addr, self.port))
        self.server.listen(1)

    def conexion(self):
        print("Conectando...")
        while self.buscar:
            try:
                self.cliente, address = self.server.accept()
                print(f"Conectado a {address}")
                while self.buscar:
                    data = self.cliente.recv(self.buf_size)
                    if data:
                        print(f"Message: {data.decode('utf-8')}")
            except socket.error as e:
                self.ob.value = False
                print(f"Estatus conexión: {e}")
                if self.cliente:
                    self.cerra_conexion()
            except Exception as e:
                self.ob.value = False
                print(f"Estatus conexión: {e}")
                if self.cliente:
                    self.cerra_conexion()
                break
        self.cerra_conexion()

    def iniciar_conexion(self):
        self.hilo = Thread(target=self.conexion)
        self.hilo.daemon = True
        self.hilo.start()

    def enviar_mensaje(self, mssg):
        if self.cliente:
            try:
                self.cliente.send(mssg.encode("utf-8"))
            except Exception as e:
                self.ob.value = False
                print(f"Error al enviar el mensaje: {e}")

    def cerra_conexion(self):
        self.buscar = False
        if self.cliente:
            self.cliente.close()

    def busqueda(self):
        self.buscar = False if self.buscar else True
        print(self.buscar)
        if self.buscar:
            self.ob.value = True
            self.iniciar_conexion()
        else:
            self.ob.value = False
            self.cerra_conexion()
