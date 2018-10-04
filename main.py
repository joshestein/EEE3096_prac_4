import RPi.GPIO as GPIO

# Constants
#--------------------

secure_btn = 23

#--------------------

# Setup
#--------------------

GPIO.setmode(GPIO.BCM)
GPIO.setup(secure_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)

