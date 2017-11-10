import socket
from multiprocessing import Process, Manager
import pygame
import os
from time import sleep

'''

    Writen by Gunnar Bjorkman for robot control over raspberrypi connection

    Current design:
    Send and recieve server data over socket connection that was gathered from
    a 'Logitech Extreme 3D Pro' and display over pygame window

    UPDATES:


'''


### Client Stuff
SERVER = "127.0.0.1"  # 169.254.209.111
PORT = 6762
s = socket.socket()
s.connect((SERVER, PORT))


def messageCatcher(info, _):
    while True:

        data = s.recv(1024)

        data_list = data.split(";")

        i_val = 0
        for i in range(len(data_list)):

            msg = data_list[i_val]

            if msg != "ping" and msg != "":

                if msg.startswith("battery:"):
                    title, value = msg.split(':')
                    info["battery"] = float(value)

            i_val += 1


def mainProcess(info, _):

    # Init pygame
    pygame.init()

    white = (255, 255, 255)
    black = (0, 0, 0)

    ### Define some pygame stuff
    size = width, height = 720, 480
    screen = pygame.display.set_mode(size)
    pygame.joystick.init()
    clock = pygame.time.Clock()
    pygame.font.init()
    myfont = pygame.font.SysFont('Arial', 48)
    screen = pygame.display.set_mode((600,400), 0, 32)
    screen.fill((white))
    pygame.display.update()

    # let server console know we're here
    s.sendall('client initiate')

    x_axis = 0
    y_axis = 0
    z_axis = 0
    switch_axis = 0

    def send(msg):
        s.sendall(msg)


    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                send('client terminate')
                pygame.quit()
                quit()

        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        name = joystick.get_name()
        axes = joystick.get_numaxes()
        buttons = joystick.get_numbuttons()
        hats = joystick.get_numhats()

        x_axis = joystick.get_axis(0)
        y_axis = joystick.get_axis(1)
        z_axis = joystick.get_axis(2)
        switch_axis = joystick.get_axis(3)

        for i in range( buttons ):
            button = joystick.get_button( i )
            print("Button {:>2} value: {}".format(i,button) )

        for i in range( hats ):
            hat = joystick.get_hat( i )
            print("Hat {} value: {}".format(i, str(hat)) )

        print("")
        print("x_axis", round(x_axis, 2))
        window_x_axis_text = myfont.render(str(x_axis), 1, (black)) # Write value to pygame window
        print("y_axis", round(y_axis, 2))
        window_y_axis_text = myfont.render(str(y_axis), 1, (black)) # Write value to pygame window
        print("z_axis", round(z_axis, 2))
        window_z_axis_text = myfont.render(str(z_axis), 1, (black)) # Write value to pygame window
        print("switch_axis", round(switch_axis, 2))
        window_switch_axis_text = myfont.render(str(switch_axis), 1, (black)) # Write value to pygame window

        data_string = "data: "+str(round(x_axis, 2))+" "+str(round(y_axis, 2))+" "+str(round(z_axis, 2))+" "+str(round(switch_axis, 2))+";"
        print data_string
        print("")
        print(info['battery'])

        send(data_string)

        # Render stuff on screen

        screen.blit(window_x_axis_text, (10, 10))
        screen.blit(window_y_axis_text, (10, 40))
        screen.blit(window_z_axis_text, (10, 70))
        screen.blit(window_switch_axis_text, (10, 100))
        pygame.display.update()

        clock.tick(20)
        os.system('clear')  # Clear screen for Mac and Linux
        screen.fill((white))
        #os.system('cls')  # Clear screen for Windows


if __name__ == "__main__":
    manager = Manager()

    info = manager.dict()

    info['battery'] = 0
    info['shoulder_pivot'] = 0
    info['z_axis'] = 0
    info['switch_axis'] = 0
    info['terminator_var'] = 0

    # - multiprocessing runs a separate instance of python, typical
    #   global variables are not shared between child processes
    mC = Process(target=messageCatcher, args=(info, 1))
    mP = Process(target=mainProcess, args=(info, 1))
    mC.start()
    mP.start()
    mC.join()
    mP.join()
