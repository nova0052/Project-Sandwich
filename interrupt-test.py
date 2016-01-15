import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def cb_green_down(dummy):
    print "You pressed the green button!"

def cb_green_up(dummy):
    print "You released the green button!"

def cb_red_down(dummy):
    print "You pressed the red button!"

def cb_red_up(dummy):
    print "You released the red button!"

GPIO.add_event_detect(12, GPIO.FALLING, callback=cb_green_down, bouncetime=300)
#GPIO.add_event_detect(12, GPIO.RISING, callback=cb_green_up)
GPIO.add_event_detect(16, GPIO.FALLING, callback=cb_red_down, bouncetime=300)
#GPIO.add_event_detect(16, GPIO.RISING, callback=cb_red_up)

try:
    pwd = raw_input("What's the password?")
    print "Nope! %s isn't it!" %pwd
    
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()
