import RPi.GPIO as GPIO
import Adafruit_MCP3008

# Constants
#--------------------
secure_btn = 23
CLK = 21
MOSI = 20
MISO = 19
CS = 26

def setup():
    """Setup button, MCP and pot."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(secure_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

def main():
    setup()
    #TODO

if name == "__main__":
    main()

