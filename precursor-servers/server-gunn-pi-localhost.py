import socket
from multiprocessing import Process, Manager
import time
import sys
import os

'''

    !!!THIS FILE IS FOR LOCALHOST TESTING!!!

    Writen by Gunnar Bjorkman to control a robot via raspberrypi

    Current design:

    * Recieve client's inputs and send server/robot info to client over socket
    connection.
    * Controls ESCs and servos that are plugged into the GPIO ports on the
    raspberrypi.
    * Uses TCP bi-directional connection (both server and client can send and
    recieve data).
    * Multiprocessing so the server can listen for messages and control the
    robot simultaneously.

    Copy file over ssh to raspberrypi:

    scp {PATH TO THIS} pi@raspberrypi:~/Desktop/

    *** this exact command is for my computer only, use: ***

    scp ~/Documents/Code/python/gunn-pi/{THIS}.py pi@raspberrypi:~/Desktop/


'''


### Server Stuff
SERVER = "127.0.0.1"  # 169.254.209.111
PORT = 6762
s = socket.socket()
s.bind((SERVER, PORT))
s.listen(1024)


def messageCatcher(inputs, _):
    while True:

        c, addr = s.accept()     # Establish connection with client.

        try:
            print 'client connected:'+str(addr)
            while True:
                data = c.recv(1024)
                #print data

                if data.startswith("data:"):
                    data, _ = data.split(';', 1)
                    _, x_axis, y_axis, z_axis, switch_axis = data.split()
                    inputs['x_axis'] = float(x_axis)
                    inputs['y_axis'] = float(y_axis)
                    inputs['z_axis'] = float(z_axis)
                    inputs['switch_axis'] = float(switch_axis)

                c.sendall("battery:"+str(inputs['battery'])+";")

                if data:
                    c.sendall('ping;')
                else:
                    print 'Donnection died'
                    break

        finally:
            c.close()


def mainProcess(inputs, _):

    ### Variables global to the main process
    # Base Control
    m1 = 7;
    m2 = 7;
    m3 = 7;
    m4 = 7;

    # Negates inputs within the threshold and returns remaining values as
    # their corresponding -1 through 1 values. And rounds to two decimals.
    #
    # Only useful for analog/axial inputs
    '''
        # depreciated method
        def inputFilter(x):
            # shift values
            if(x <= -0.05):
                x += 0.05
            if(x >= 0.05):
                x -= 0.05
            if(x < 0.05 and x > -0.05):
                x = 0
            # max values
            if(x == 0.95):
                x = 1
            if(x == -0.95):
                x = -1
            return x
    '''
    def inputFilter(x):
        thresh_hold = 0.1
        if x < 0:
            thresh_hold = -thresh_hold
            x = min(thresh_hold, x)
            x = x - thresh_hold
            ratio = 1 / (1 - abs(thresh_hold))
            x = x * ratio
        else:
            x = max(thresh_hold, x)
            x = x - thresh_hold
            ratio = 1 / (1 - abs(thresh_hold))
            x = x * ratio
        return round(x, 2)


    while True:

        # Filter the inputs through 'inputFilter()'
        x_axis = inputFilter(inputs['x_axis'])
        y_axis = inputFilter(inputs['y_axis'])
        z_axis = inputFilter(inputs['z_axis'])
        switch_axis = inputFilter(inputs['switch_axis'])

        print(x_axis)
        print(y_axis)
        print(z_axis)
        print(switch_axis)

        horizontal_power = (x_axis * 4) + 7
        vertical_power = (y_axis * 4) + 7

        print("longitudinal movement: " + str(vertical_power))
        print("strafe movement: " + str(horizontal_power))
        print(" ")
        m1 = min(11, max(3, (-1 * (x_axis - (-1 * z_axis)) * 4) + 7))
        m3 = min(11, max(3, ( 1 * (x_axis + (-1 * z_axis)) * 4) + 7))
        m2 = min(11, max(3, (-1 * (y_axis - (-1 * z_axis)) * 4) + 7))
        m4 = min(11, max(3, ( 1 * (y_axis + (-1 * z_axis)) * 4) + 7))
        # m4 = (-1 * (inputs['y_axis'] - inputs['z_axis'] / 4) * 4) + 7
        print("Motor 1: " + str(m1))
        print("Motor 2: " + str(m2))
        print("Motor 3: " + str(m3))
        print("Motor 4: " + str(m4))

        if horizontal_power > 10:
            inputs['battery'] = 1
            print 'battery = 1'
        else:
            inputs['battery'] = 0
            print 'battery = 0'

        #m1.ChangeDutyCycle(horizontal_power)  # between 2.5 & 12.5


        time.sleep(0.05)
        os.system('clear')  # Clear screen for Mac and Linux

if __name__ == "__main__":
    manager = Manager()

    inputs = manager.dict()

    inputs['x_axis'] = 0
    inputs['y_axis'] = 0
    inputs['z_axis'] = 0
    inputs['switch_axis'] = 0
    inputs['battery'] = 0

    # - multiprocessing runs a separate instance of python, typical
    #   global variables are not shared between child processes
    mC = Process(target=messageCatcher, args=(inputs, 1))
    mP = Process(target=mainProcess, args=(inputs, 1))
    mC.start()
    mP.start()
    mC.join()
    mP.join()
