import pygame, sys
from pygame.locals import *

# define variables
green = (  0, 255,   0)
red   = (255,   0,   0)
blue  = (  0,   0, 255)
black = (  0,   0,   0)
white = (255, 255, 255)

# draw the screen
Screen = pygame.display.set_mode((800, 600))
Screen.fill(black)

# draw the joystick input area
stick_box = pygame.Rect(50, 150, 300, 300)
pygame.draw.rect(Screen, green, stick_box, 0)
pygame.draw.circle(Screen, blue, (200, 300), 10, 0)
# draw the motor output area
motorL = pygame.Rect(500, 150, 75, 300)
pygame.draw.rect(Screen, green, motorL, 0)
motorR = pygame.Rect(625, 150, 75, 300)
pygame.draw.rect(Screen, green, motorR, 0)

# define functions
def terminate():
    pygame.quit()
    sys.exit()
    
# set up joystick
pygame.joystick.init()
control0 = pygame.joystick.Joystick(0)
control0.init()

# make a loop to hold everything
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()

# get joystick inputs and animate the screen
        elif event.type == JOYAXISMOTION:
            x_val = control0.get_axis(0)
            y_val = control0.get_axis(1)
            control0.get_axis(0)
            control0.get_axis(1)
            pygame.draw.circle(Screen, blue, ((int(x_val * 150) + 50), (int(y_val * 150) + 150)), 10, 0)

# close the loop
    pygame.display.update()
