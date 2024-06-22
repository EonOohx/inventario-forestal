import RPi.GPIO as GPIO
import time
import YB_Pcb_Car

GPIO.setmode(GPIO.BOARD)

#Definir la placa a car
car = YB_Pcb_Car.YB_Pcb_Car()

# Ignore the warning messages
GPIO.setwarnings(False)

# Define the pins of the ultrasonic module
EchoPin = 18
TrigPin = 16
Buzzer = 32

# Definir las melodías para el buzzer
tune = [2637, 2637, 2637, 2093, 2637, 3136, 1568, 2093, 1568, 1319, 1760, 1976, 1865, 1760, 1568, 2637, 3136, 3520, 2794, 3136, 2637, 2093, 2349, 1976]
durt = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
# Set the pin mode of the ultrasonic module
GPIO.setmode(GPIO.BOARD)
GPIO.setup(EchoPin, GPIO.IN)
GPIO.setup(TrigPin, GPIO.OUT)
#GPIO.setup(Buzzer, GPIO.OUT)  # Configura el pin del buzzer como salida
#Buzz = GPIO.PWM(Buzzer, 440)  # Inicializa el PWM en el pin del buzzer con una frecuencia inicial de 440 Hz



def Distance():
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TrigPin, GPIO.LOW)

    t3 = time.time()

    while not GPIO.input(EchoPin):
        t4 = time.time()
        if (t4 - t3) > 0.03:
            return -1
    t1 = time.time()
    while GPIO.input(EchoPin):
        t5 = time.time()
        if (t5 - t1) > 0.03:
            return -1

    t2 = time.time()
    return ((t2 - t1) * 340 / 2) * 100

def Distance_test():
    num = 0
    ultrasonic = []
    while num < 5:
        distance = Distance()
        while int(distance) == -1:
            distance = Distance()
        while (int(distance) >= 500 or int(distance) == 0):
            distance = Distance()
        ultrasonic.append(distance)
        num += 1
    distance = (ultrasonic[1] + ultrasonic[2] + ultrasonic[3]) / 3
    return distance


def run_car():
    # Función para hacer avanzar el carro
    print('Adelante')
    car.Car_Run(40, 40)

def stop_car():
    # Función para detener el carro
    print('Detener')
    car.Car_Stop()
    time.sleep(1)
    
def play_buzzer(Buzz:GPIO.PWM):
    print('\nPlaying song...')
    for i in range(len(tune)):
        Buzz.ChangeFrequency(tune[i])  
        time.sleep(durt[i] * .2)    

'''def check_distance_and_sound():
    distance = Distance_test()
    print("Distancia medida:", distance, "cm")
    if distance <= 20:  
        stop_car()
        Buzz.start(50)
        play_buzzer()
        Buzz.stop()  # Detener buzzer
    else:
        run_car()
        time.sleep(2)  # Espera 2 segundos antes de la siguiente medición

def iniciar_ultrasonico():
    try:
        while True:
            print("Tomando una medición...")
            check_distance_and_sound()
            time.sleep(1)  # Espera 2 segundos antes de la siguiente medición
    except KeyboardInterrupt:
        print("Medición detenida por el usuario")
        GPIO.cleanup()
'''