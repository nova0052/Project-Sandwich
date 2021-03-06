import RPi.GPIO as GPIO
import socket
import sys
import subprocess

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

# function to concatenate control commands into a single string
ynx = ""
def stringulate(cmd, ynx):
    if cmd >-1:
        ynx += "+" + str(cmd)
        return ynx
    else:
        ynx += str(cmd)
        return ynx


#function for LED status commands
LEDStatus = 0
def LED_func(channel):
    global LEDStatus
    if not GPIO.input(21):
        LEDStatus += 1
        if LEDStatus > 3:
            LEDStatus = 0
    else:
        return
#function to switch cameras (currently using green button)
cam_select = 0
def cam_select_func(channel):
    global cam_select
    if not GPIO.input(12):
        cam_select =+ 1
        if cam_select > 1:
            cam_select = 0
    else:
        return
#function for left trigger (not currently in use, see camera switch function above)
l_trig = "off"
def L_Trig_func(channel):
    global l_trig
    if not GPIO.input(12):
        l_trig = "on"
    else:
        l_trig = "off"
#function for red (right) button. temporarily used instead of right trigger
r_trig = "off"
def R_Trig_func(channel):
    global r_trig
    if not GPIO.input(16):
        r_trig = "on"
    else:
        r_trig = "off"

#function for blue (top) button. temporarily used as on/off switch
def PWR_func(channel):
    if not GPIO.input(20):
        print "\rShutting down unless power button is released within 5 seconds.\n"
        time.sleep(5)
        if GPIO.input(20):
            return
        else:
            print "Powering Off!"
            os.system("shutdown -h now")

#function for left trigger button (not currently in use)


#function for right trigger button (not currently in use)





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
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#set up the callbacks for button presses on each input pin
GPIO.add_event_detect(21, GPIO.BOTH, callback=LED_func, bouncetime=50)
GPIO.add_event_detect(20, GPIO.BOTH, callback=PWR_func, bouncetime=50)
GPIO.add_event_detect(12, GPIO.BOTH, callback=cam_select_func, bouncetime=50)
GPIO.add_event_detect(16, GPIO.BOTH, callback=R_Trig_func, bouncetime=50)

# joystick ADC channels
joy_x_adc = 0
joy_y_adc = 1


# create the socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

host = "DevProto.local"
port = 17004

videofeed = subprocess.Popen("gst-launch-1.0 udpsrc port=9000 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! queue max-size-time=100 ! eglglessink sync=false", shell = True)

while True:
    try:
        # make sure the video is running
        vid_status = videofeed.poll()
        if vid_status != None:
            videofeed = subprocess.Popen("gst-launch-1.0 udpsrc port=9000 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! queue max-size-time=100 ! eglglessink sync=false", shell = True)
        
	# get joystick position from ADC
        joy_x = readadc(joy_x_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        joy_y = readadc(joy_y_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

        # convert the ADC values to something the motor driver can use
        joy_x = (joy_x - 525)
        joy_y = (joy_y - 521)

        #combine the joystick x and y values into a string
        temp = ""

        temp += stringulate(joy_x, ynx).zfill(4)
        temp += stringulate(joy_y, ynx).zfill(4)

        #add button statuses to the end of the string
        """if l_trig =="on":
            temp += "1"
        else:
            temp += "0" """
        temp += str(cam_select)
        if r_trig =="on":
            temp += "1"
        else:
            temp += "0"
        temp += str(LEDStatus)
        sys.stdout.write("\r%s" % temp)
        sys.stdout.flush()

        try:
            sock.sendto(str(temp), (host, port))
            #d = sock.recvfrom(1024)
            #reply = d[0]
            #addr = d[1]

            #print "Server reply:", reply

        except socket.error, msg:
            print "Error " +str(msg[0])+ ": " +msg[1]
            sys.exit()
    except KeyboardInterrupt:
        print "\nHalted by user!"
        GPIO.cleanup()
        sys.exit()
