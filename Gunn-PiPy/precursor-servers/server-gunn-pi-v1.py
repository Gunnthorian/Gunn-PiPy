import socket
from multiprocessing import Process, Manager
import time
import sys
import os

'''

scp ~/Documents/Code/python/client-server_simple/server.py pi@raspberrypi:~/Desktop/


'''

### Server Stuff
HOST = "169.254.209.111"  # 169.254.209.111
PORT = 6789
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))



def messageCatcher(inputs, _):
    while True:
        data, addr = s.recvfrom(1024)

        if data == "key_left_down":
            inputs['k_left'] = 1
            print('left')
        if data == "key_right_down":
            inputs['k_right'] = 1
            print('right')
        if data == "key_left_up":
            inputs['k_left'] = 0
        if data == "key_right_up":
            inputs['k_right'] = 0

        if data == "terminate":
            inputs['terminator_var'] = 1
            print 'Client terminated... :('
        if data == "Client is connected...":
            inputs['terminator_var'] = 0
            print 'Client joined...'

        if data.startswith("data:"):
            _, x_axis, y_axis, z_axis, switch_axis = data.split()
            inputs['x_axis'] = float(x_axis)
            inputs['y_axis'] = float(y_axis)
            inputs['z_axis'] = float(z_axis)
            inputs['switch_axis'] = float(switch_axis)




def mainProcess(inputs, _):

    ### Variables global to the main process
    # Base Control
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT) # motor 1
    GPIO.setup(18, GPIO.OUT) # motor 2
    GPIO.setup(27, GPIO.OUT) # motor 3
    GPIO.setup(22, GPIO.OUT) # motor 4
    m1 = GPIO.PWM(17, 50)
    m2 = GPIO.PWM(18, 50)
    m3 = GPIO.PWM(27, 50)
    m4 = GPIO.PWM(22, 50)

    m1.start(7)
    m2.start(7)
    m3.start(7)
    m4.start(7)

    def inputFilter(x):
        if(x <= -0.05):
            x += 0.05
        if(x >= 0.05):
            x -= 0.05
        if(x < 0.05 and x > -0.05):
            x = 0
        if(x == 0.95):
            x = 1
        if(x == -0.95):
            x = -1
        return x

    while True:
        #if inputs['k_left'] == 1:

        # filtered inputs
        x_axis = inputFilter(inputs['x_axis'])
        y_axis = inputFilter(inputs['y_axis'])
        z_axis = inputFilter(inputs['z_axis'])
        switch_axis = inputFilter(inputs['switch_axis'])

        print(x_axis)
        print(y_axis)
        print(z_axis)
        print(switch_axis)

        horizontal_power = (inputs['x_axis'] * 4) + 7
        vertical_power = (inputs['y_axis'] * 4) + 7

        print("longitudinal movement: " + str(vertical_power))
        print("strafe movement: " + str(horizontal_power))
        print(" ")
        m1_duty_cycle = min(11, max(3, (-1 * (inputs['x_axis'] - (-1 * inputs['z_axis'] )) * 4) + 7))
        m3_duty_cycle = min(11, max(3, ( 1 * (inputs['x_axis'] + (-1 * inputs['z_axis'] )) * 4) + 7))
        m2_duty_cycle = min(11, max(3, (-1 * (inputs['y_axis'] - (-1 * inputs['z_axis'] )) * 4) + 7))
        m4_duty_cycle = min(11, max(3, ( 1 * (inputs['y_axis'] + (-1 * inputs['z_axis'] )) * 4) + 7))
        # m4 = (-1 * (inputs['y_axis'] - inputs['z_axis'] / 4) * 4) + 7
        print("Motor 1: " + str(m1_duty_cycle))
        print("Motor 2: " + str(m2_duty_cycle))
        print("Motor 3: " + str(m3_duty_cycle))
        print("Motor 4: " + str(m4_duty_cycle))

        m1.ChangeDutyCycle(m1_duty_cycle)
        m2.ChangeDutyCycle(m2_duty_cycle)
        m3.ChangeDutyCycle(m3_duty_cycle)
        m4.ChangeDutyCycle(m4_duty_cycle)

        #m1.ChangeDutyCycle(horizontal_power)  # between 2.5 & 12.5


        time.sleep(0.01)
        os.system('clear')  # Clear screen for Mac and Linux
        if inputs['terminator_var'] == 1:
            print 'Client is missing, we will pause\n' \
                  'and wait for them to reconnect\n' \
                  'before doing anything irrational.'
            # Default all values so robot is safe

if __name__ == "__main__":
    manager = Manager()

    inputs = manager.dict()

    inputs['x_axis'] = 0
    inputs['y_axis'] = 0
    inputs['z_axis'] = 0
    inputs['switch_axis'] = 0
    inputs['terminator_var'] = 0

    # - multiprocessing runs a separate instance of python, typical
    #   global variables are not shared between child processes
    mC = Process(target=messageCatcher, args=(inputs, 1))
    mP = Process(target=mainProcess, args=(inputs, 1))
    mC.start()
    mP.start()
    mC.join()
    mP.join()
