import RPi.GPIO as GPIO
import Adafruit_MCP3008
from timeit import default_timer as timer

# Constants
#--------------------
secure_btn = 23
start_stop_btn = 24

CLK = 21
MOSI = 20
MISO = 19
CS = 26
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

start = True
begin = 0.0
end = 0.0

def start_stop_callback(channel):
    global start, begin
    if start:
        start = False
    else:
        start = True
        begin = timer()

def setup():
    """Setup button, MCP and pot."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(secure_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(start_stop_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    GPIO.add_event_detect(start_stop_btn, GPIO.FALLING, callback=start_stop_callback, bouncetime=300)

def main():
    setup()
    while start:
        ### if pot input restart time
        end = timer()

        if (end-begin) > 2:
            start = False

if name == "__main__":
    main()

