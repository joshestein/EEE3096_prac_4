import RPi.GPIO as GPIO
import Adafruit_MCP3008
from timeit import default_timer as timer
import time

# Constants
#--------------------
secure_btn = 23
start_stop_btn = 24
LED_unlock = 2
LED_lock = 3

CLK = 11
MOSI = 10
MISO = 9
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

pot_channel = 5

prev_voltage = 0
start = True
begin = 0.0
end = 0.0

def start_stop_callback(channel):
    global start, begin
    if start:
        start = False
    else:
        start = True
        begin = time.time()

def setup():
    """Setup button, MCP and pot."""
    global begin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(secure_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(start_stop_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    GPIO.setup(LED_unlock, GPIO.OUT)
    GPIO.setup(LED_lock, GPIO.OUT)
    
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)


    GPIO.add_event_detect(start_stop_btn, GPIO.FALLING, callback=start_stop_callback, bouncetime=300)
    begin = timer()

def read_pot(pot_voltage):
    if pot_voltage > prev_voltage:
        prev_voltage = pot_voltage
        return "L"
    else:
        prev_voltage = pot_voltage
        return "R"

def main():
    global start, begin, end
    setup()
    print("Start: "+str(start))

    while start:
        pot_voltage = mcp.read_adc(pot_channel)

        ### if pot input restart time
        end = timer()

        if (end-begin) > 2:
            start = False

if __name__ == "__main__":
    main()

