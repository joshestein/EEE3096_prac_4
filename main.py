import RPi.GPIO as GPIO

# Constants
#--------------------

secure_btn = 23

#--------------------

# Setup
#--------------------
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(secure_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def main():
    setup()
    #TODO

if name == "__main__":
    main()

