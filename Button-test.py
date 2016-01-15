import RPi.GPIO as GPIO
import sys

#

# set GPIO pins as inputs
GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# define a variable for each button
l_trig = ""
r_trig = ""

# tie the button states and variables together

# check the button states
while True:
    try:
    
        if (GPIO.input(12)):
            l_trig = "off"
        else:
            l_trig = "on"

        if (GPIO.input(16)):
            r_trig = "off"
        else:
            r_trig = "on"
    
# display when each button is pressed and released
        if l_trig == "on":
            print "Left Trigger pressed!"
        if r_trig == "on":
            print "Right Trigger pressed!"


    
    except KeyboardInterrupt:
        print "Halted by user!"
        GPIO.cleanup()
