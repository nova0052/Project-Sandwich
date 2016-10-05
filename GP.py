import RPi.GPIO as GPIO
import socket
import sys
import subprocess

GPIO.setmode(GPIO.BCM)

# callback function for power switch
def PWR_func(channel):
    if not GPIO.input(4):
        print "Powering Off!"
        os.system("shutdown -h now")

# set up the pins
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(4, GPIO.FALLING, callback=PWR_func, bouncetime=50)

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

cam_last = 0

host = ""
port = 17004

# make the socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

# bind the socket
try:
    sock.bind(host, port)
except socket.error, msg:
    print 'Bind failed. Error ' + str(msg[0]) + ' Message '+msg[1]
    sys.exit()

print 'Socket bind complete'

# talk to the client
while True:
    # receive data from client
    d = ''
    d = sock.recvfrom(11)
    ynx = d[0]
    addr = d[1]
    # harshly rip the commands from the comfort of their string
    joy_x = int(ynx[0:4])
    joy_y = int(ynx[4:8])
    l_trig = int(ynx[8])
    r_trig = int(ynx[9])
    led = int(ynx[10])

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

    #check for triggers and do stuff (under construction)
    """ if l_trig == 1:
        print "Switch Camera!" """

    if l_trig == 1:
        if l_trig != cam_last:
            camfeed0.kill()
            camfeed1 = subprocess.Popen('sudo raspivid -cs 1 -h 640 -w 800 -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay! udpsink host=raspberrypi.local port=44444', shell=True)
            cam_last = 1

    if l_trig == 0:
        if l_trig != cam_last:
            camfeed1.kill()
            camfeed1 = subprocess.Popen('sudo raspivid -cs 0 -h 640 -w 800 -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay! udpsink host=raspberrypi.local port=44444', shell=True)
            cam_last = 0
    
    if r_trig == 1:
        # placeholder for output to zapper circuit
        print "ZAP! KILL!"
        
    
    mot_msg = 'Motor Outputs: R: ', motor_R , 'L: ', motor_L
    print mot_msg

sock.close()
