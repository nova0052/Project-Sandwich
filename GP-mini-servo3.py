import RPIO
import os

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

RPIO.add_event_detect(4, PWR_func, edge="falling" debounce_timeout_ms=50)

# set up the PWM outputs to the motors 

pwm_MF = RPIO.PWM(19, 100)
pwm_MR = RPIO.PWM(26, 100)
servo = PWM.Servo()

pwm_MF.start(0)
pwm_MR.start(0)
servo.set_servo(20, 1450)

# joystick ADC channels
joy_x_adc = 0
joy_y_adc = 1

while True:
    # get joystick position from ADC
    joy_x = readadc(joy_x_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    joy_y = readadc(joy_y_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

    # convert the ADC values to something the motor driver can use
    joy_x = (joy_x - 525)
    joy_y = (joy_y - 521)

    motor_DC = float(joy_y)/512
    servo_pos = (float(joy_x)/512) * 650


    if motor_DC > 1:
        motor_DC = 1
    if motor_DC < -1:
        motor_DC = -1

    MF = motor_DC * 100
    MR = motor_DC * -100

       
    # send commands out to the motors
    servo.set_servo(1450 + servo_pos)
    if motor_DC > 0:
        pwm_MR.ChangeDutyCycle(0)
        pwm_MF.ChangeDutyCycle(MF)
    if motor_DC <= 0:
        pwm_MF.ChangeDutyCycle(0)
        pwm_MR.ChangeDutyCycle(MR)
