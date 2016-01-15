import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def cb_green(dummy):
    if not GPIO.input(12):
        print "You pressed the green button!"
    else:
        print "You released the green button!"

def cb_red(dummy):
    if not GPIO.input(16):
        print "You pressed the red button!"
    else:
        print "You released the red button!"

GPIO.add_event_detect(12, GPIO.BOTH, callback=cb_green, bouncetime=100)
GPIO.add_event_detect(16, GPIO.BOTH, callback=cb_red, bouncetime=100)

try:
    pwd = raw_input("What's the password?\n")
    print "Nope! %s isn't it!" %pwd
    
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()
