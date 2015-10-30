import os
import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# function to read SPI data from MCP3008
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum >7) or (adcnum <0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False) # start clock low
    GPIO.output(cspin, False) # bring CS low

    commandout = adcnum
    commandout |= 0x18 # start bit + single-ended bit
    commandout <<= 3 # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<=1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one  null bit, and 10 ADC bits
    for i in range (12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)
    adcout >>=1 # first bit is 'null' and gets dropped
    return adcout

# function for joystick deadzones (in progress)
# def deadzone(stickvalue):
        

# define which pins are being used
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# set up the PWM outputs to the motors (in progress)
#PWM_FREQ = 0
#pwm_L = GPIO.PWM("pin number", PWM_FREQ)
#pwm_R = GPIO.PWM("pin number", PWM_FREQ)

# joystick ADC channels
joy_x_adc = 0
joy_y_adc = 1

while True:
    joy_x = readadc(joy_x_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    joy_y = readadc(joy_y_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

    # convert the ADC values to something the motor driver can use
    joy_x = (joy_x - 512)
    joy_y = (joy_y - 512)
    
    motor_L = float(joy_y + joy_x)/511
    motor_R = float(joy_y - joy_x)/511
    
    # send commands out to the motors

    # put joystick position on the screen
    if DEBUG:
        print "Joy X", joy_x, "Joy Y", joy_y, "Motor L", motor_L, "Motor R", motor_R
        
