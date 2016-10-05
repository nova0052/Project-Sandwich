import RPIO as GPIO
import os

GPIO.setmode(GPIO.BCM)

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

# callback function for power switch
def PWR_func(channel):
    if not GPIO.input(4):
        print "Powering Off!"
        os.system("shutdown -h now")

# define which pins are being used
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(4, GPIO.FALLING, callback=PWR_func, bouncetime=50)

# set up the PWM outputs to the motors 

pwm_MF = GPIO.PWM(19, 100)
pwm_MR = GPIO.PWM(26, 100)
pwm_servo = GPIO.PWM(20, 50)

pwm_MF.start(0)
pwm_MR.start(0)
pwm_servo.start(7)

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
    servo_pos = (float(joy_x)/512) * 4.5


    if motor_DC > 1:
        motor_DC = 1
    if motor_DC < -1:
        motor_DC = -1

    MF = motor_DC * 100
    MR = motor_DC * -100

       
    # send commands out to the motors
    pwm_servo.ChangeDutyCycle(7 + servo_pos)
    if motor_DC > 0:
        pwm_MR.ChangeDutyCycle(0)
        pwm_MF.ChangeDutyCycle(MF)
    if motor_DC <= 0:
        pwm_MF.ChangeDutyCycle(0)
        pwm_MR.ChangeDutyCycle(MR)
