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

pot_channel = 0

pot_tolerance = 20
time_tolerance = 0.05
start = True
secure = False
begin = 0.0
end = 0.0
user_times = []
user_directions = []

code_times = [200, 200, 1000] #in ms
code_directions = ["L", "L", "R"]

def start_stop_callback(channel):
    global start, begin
    if start:
        start = False
    else:
        start = True
        begin = time.time()

def secure_insecure_callback(channel):
    global secure
    if secure:
        secure = False
    else:
        secure = True

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
    GPIO.add_event_detect(secure_btn, GPIO.FALLING, callback=secure_insecure_callback, bouncetime=300)

def get_direction(start_voltage, end_voltage):
    if start_voltage > end_voltage:
        return "L"
    else:
        return "R"

def check_times(secure):
    global user_times, code_times
    if secure == False:
        #TODO: sort user times, code times
    for i in range(0, len(user_times)):
        if user_times[i] != code_times[i]:
            return False 
    return True

def check_positions(secure):
    global user_positions, code_positions
    if secure == False:
        #TODO: sort user positions, code_positions
    for i in range(0, len(user_positions)):
        if user_positions[i] != user_positions[i]:
            return False 
    return True

def main():
    global start, begin, end, secure
    setup()

    pot_voltage = mcp.read_adc(pot_channel)
    prev_voltage = pot_voltage
    

    while start:
        while abs(pot_voltage - prev_voltage) < tolerance:
            # wait while pot is not moving
            start_voltage = mcp.read_adc(pot_channel)

            ### if pot input restart time
            end = timer()
            new_value = False
            if (end-begin) > 2:
                start = False
                break

        begin = timer()
        while abs(pot_voltage - prev_voltage) > tolerance:
            # wait while pot is moving
            end_voltage = mcp.read_adc(pot_channel)
            new_value = True
    
        end = timer()
        if new_value:
            user_times.append(end-begin)
            user_directions.append(get_direction(start_voltage, end_voltage))§
            new_value = False

    
    if (check_times(secure) and check_positions(secure)):
        #TODO: success!
    else:
        #TODO: waa waa waaaaa    

if __name__ == "__main__":
    main()

