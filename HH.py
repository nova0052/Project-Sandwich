import RPi.GPIO as GPIO
import socket
import sys


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

# function to concatenate control commands into a single string
#def stringulate(cmd, dat):
#    if cmd >= 0:
#        dat += "+" + str(cmd)
#    else:
#        dat += str(cmd)


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

# joystick ADC channels
joy_x_adc = 0
joy_y_adc = 1


# create the socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

host = 'localhost'
port = 7004

ynx = ""

while True:
    joy_x = readadc(joy_x_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
    joy_y = readadc(joy_y_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

    # convert the ADC values to something the motor driver can use
    joy_x = (joy_x - 525)
    joy_y = (joy_y - 521)

    if joy_x >-1:
        ynx += "+" + str(joy_x)
    else:
        ynx += str(joy_x)

    if joy_y >-1:
        ynx += "+" + str(joy_y)
    else:
        ynx += str(joy_y)

    print "Joy X", joy_x, "Joy Y", joy_y

    try:
        sock.sendto(str(ynx), (host, port))
        d = sock.recvfrom(1024)
        reply = d[0]
        addr = d[1]

        print 'Server reply:' + reply

    except socket.error, msg:
        print 'Error ' +str(msg[0])+ ': ' +msg[1]
        sys.exit()
