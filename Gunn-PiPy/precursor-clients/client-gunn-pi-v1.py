import socket
import pygame
import os
from time import sleep

'''

   Writen by Gunnar Bjorkman for robot control over raspberrypi connection

   Current design:
   Send server data over socket connection that was gathered from a 'Logitech Extreme 3D Pro'

'''

# Init pygame
pygame.init()

### Client Stuff
HOST = "localhost"  # 169.254.209.111
PORT = 6789
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

### Define some pygame stuff
size = width, height = 320, 240
screen = pygame.display.set_mode(size)
pygame.joystick.init()
clock = pygame.time.Clock()

# let server console know we're here
s.sendto('Client is connected...', (HOST, PORT))

x_axis = 0
y_axis = 0
z_axis = 0
switch_axis = 0


def send(msg):
    s.sendto(msg, (HOST, PORT))


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            send('terminate')
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
    print("y_axis", round(y_axis, 2))
    print("z_axis", round(z_axis, 2))
    print("switch_axis", round(switch_axis, 2))

    data_string = "data: "+str(round(x_axis, 2))+" "+str(round(y_axis, 2))+" "+str(round(z_axis, 2))+" "+str(round(switch_axis, 2))
    print data_string

    send(data_string)

    clock.tick(20)
    os.system('clear')  # Clear screen for Mac and Linux

    #os.system('cls')  # Clear screen for Windows
