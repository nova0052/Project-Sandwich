import RPIO
from RPIO import PWM
import os
import sys

RPIO.setmode(RPIO.BCM)

# function to read SPI data from MCP3008
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum >7) or (adcnum <0)):
        return -1
    RPIO.output(cspin, True)

    RPIO.output(clockpin, False) # start clock low
    RPIO.output(cspin, False) # bring CS low

    commandout = adcnum
    commandout |= 0x18 # start bit + single-ended bit
    commandout <<= 3 # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            RPIO.output(mosipin, True)
        else:
            RPIO.output(mosipin, False)
        commandout <<=1
        RPIO.output(clockpin, True)
        RPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one  null bit, and 10 ADC bits
    for i in range (12):
        RPIO.output(clockpin, True)
        RPIO.output(clockpin, False)
        adcout <<= 1
        if (RPIO.input(misopin)):
            adcout |= 0x1

    RPIO.output(cspin, True)
    adcout >>=1 # first bit is 'null' and gets dropped
    return adcout

# callback function for power switch
def PWR_func(channel):
    if not RPIO.input(4):
        print "Powering Off!"
        os.system("shutdown -h now")

# define which pins are being used
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the pins
RPIO.setup(SPIMOSI, RPIO.OUT)
RPIO.setup(SPIMISO, RPIO.IN)
RPIO.setup(SPICLK, RPIO.OUT)
RPIO.setup(SPICS, RPIO.OUT)
RPIO.setup(19, RPIO.OUT)
RPIO.setup(26, RPIO.OUT)
RPIO.setup(16, RPIO.OUT)
RPIO.setup(20, RPIO.OUT)
RPIO.setup(4, RPIO.IN, pull_up_down=RPIO.PUD_UP)

RPIO.add_interrupt_callback(4, PWR_func, edge="falling", debounce_timeout_ms=50)

PWM.setup()
PWM.init_channel(11)
PWM.init_channel(12)
servo = PWM.Servo(dma_channel=8)
servo_pos = 1300
servo.set_servo(20, 1300)

# joystick ADC channels
joy_x_adc = 0
joy_y_adc = 1

while True:
    try:
        # get joystick position from ADC
        joy_x = readadc(joy_x_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        joy_y = readadc(joy_y_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

        # convert the ADC values to something the motor driver can use
        joy_x = (joy_x - 525)
        joy_y = (joy_y - 521)

        # set the steering servo's position
        if joy_x <= 0:
            servo_pos = float(joy_x + 1300)
        else:
            servo_pos = float(joy_x + 1300 + joy_x * 0.55)
        servo.set_servo(20, round(servo_pos, -1))
   
        # send commands out to the motors

        if joy_y > 0:
            PWM.add_channel_pulse(1, 26, 0, 0)
            PWM.add_channel_pulse(2, 19, 0, int(round(joy_y * 3.8, -1)))
        if joy_y <= 0:
            PWM.add_channel_pulse(2, 19, 0, 0)
            PWM.add_channel_pulse(1, 26, 0, int(round(joy_y * -3.8, -1)))
                        
    except KeyboardInterrupt:
        servo.stop_servo(20)
        RPIO.cleanup()
        sys.exit()
