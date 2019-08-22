import pygame
import socket
import time
from pygame.locals import*
import requests

control_IP = "169.254.202.202"
control_PORT = "8000"


def send(cmd):
    global control_IP, control_PORT

    requests.get("http://" + control_IP + ":" + control_PORT + "/keyboard/" + cmd)
        
##def control():
# Initialize the game engine
pygame.init()
 
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)
 
# Set the height and width of the screen
size   = [400, 300]
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont("consolas", 20)
 
pygame.display.set_caption("Keyboard Controller")
  
#Loop until the user clicks the close button.
done  = False
flag  = None
clock = pygame.time.Clock()

    
 
while not done:
 
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)
     
    # Main Event Loop
    for event in pygame.event.get(): # User did something

    

        if event.type == pygame.KEYDOWN: # If user press a key
            pressed = pygame.key.get_pressed()

            buttons = [pygame.key.name(k) for k,v in enumerate(pressed) if v]

            flag = True

       
            print("buttons : ",buttons[0])

            if buttons[0] == 'w':
                cmd = 'F'
                send(cmd)
            elif buttons[0] == 's':
                cmd = 'B'
                send(cmd)
            elif buttons[0] == 'a':
                cmd = 'L'
                send(cmd)
            elif buttons[0] == 'd':
                cmd = 'R'
                send(cmd)
            elif buttons[0] == 'b':
                cmd = 'S'
                send(cmd)
            elif buttons[0] == 'q':
                cmd = 'q'
                send(cmd)
            
           
        elif event.type == pygame.KEYUP: # If user release what he pressed

            flag = False
            print("Key up!!")
            
            if (event.key == K_a) or (event.key == K_d):
                cmd = 'N'
                send(cmd)
            

            elif (event.key == K_w) or (event.key == K_s) or (event.key == K_b):
                cmd = 'M'
                send(cmd)

        elif event.type == pygame.QUIT:  # If user clicked close.
            done = True                 
 

 
# Be IDLE friendly
pygame.quit()


#출처: https://kkamikoon.tistory.com/132?category=797804 [컴퓨터를 다루다]
