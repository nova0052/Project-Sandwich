import RPi.GPIO as GPIO

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

# set up the PWM outputs to the motors 
PWM_FREQ = 50
pwm_LF = GPIO.PWM(19, PWM_FREQ)
pwm_LR = GPIO.PWM(26, PWM_FREQ)
pwm_RF = GPIO.PWM(16, PWM_FREQ)
pwm_RR = GPIO.PWM(20, PWM_FREQ)
pwm_LF.start(0)
pwm_LR.start(0)
pwm_RF.start(0)
pwm_RR.start(0)

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

    motor_L = float(joy_y + joy_x)/1024
    motor_R = float(joy_y - joy_x)/1024

    if motor_L > 1:
        motor_L = 1
    if motor_R > 1:
        motor_R = 1
    if motor_L < -1:
        motor_L = -1
    if motor_R < -1:
        motor_R = -1

    LF = motor_L * 100
    LR = motor_L * -100
    RF = motor_R * 100
    RR = motor_R * -100
       
       
    # send commands out to the motors
    if motor_L > 0:
        pwm_LR.ChangeDutyCycle(0)
        pwm_LF.ChangeDutyCycle(LF)
    if motor_L <= 0:
        pwm_LF.ChangeDutyCycle(0)
        pwm_LR.ChangeDutyCycle(LR)
    if motor_R > 0:
        pwm_RR.ChangeDutyCycle(0)
        pwm_RF.ChangeDutyCycle(RF)
    if motor_R <= 0:
        pwm_RF.ChangeDutyCycle(0)
        pwm_RR.ChangeDutyCycle(RR)
