import RPi.GPIO as GPIO
import socket
import sys

GPIO.setmode(GPIO.BCM)

# set up the pins
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


host = ""
port = 7004

# make the socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

# bind the socket to local host and port
try:
    sock.bind((host, port))
except socket.error, msg:
    print 'Bind failed. Error ' + str(msg[0]) + ' Message '+msg[1]
    sys.exit()

print 'Socket bind complete'

# talk to the client
while True:
    # receive data from client
    d = ''
    d = sock.recvfrom(8)
    ynx = d[0]
    addr = d[1]
    print d
    # harshly rip the commands from the comfort of their string
    joy_x = int(ynx[0:4])
    joy_y = int(ynx[4:8])

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
    
    mot_msg = 'Motor Outputs: R: ', motor_R , 'L: ', motor_L
    reply = str(mot_msg)
    sock.sendto(reply, addr)

sock.close()
