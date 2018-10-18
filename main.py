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

pot_tolerance = 30
time_tolerance = 100 #very big for testing
start = True
secure = False
begin = 0.0
end = 0.0
user_times = []
user_directions = []

code_times = [300, 300, 300] #in ms
code_directions = ["L", "L", "R"]

def reset():
    global begin, user_times, user_directions
    begin = timer()
    user_times = []
    user_directions = []

def start_stop_callback(channel):
    global start, begin
    if start:
        start = False
    else:
        start = True

def secure_insecure_callback(channel):
    global secure
    if secure:
        secure = False
        print("---------------------")
        print("Switched to INSECURE mode")
        print("---------------------")
    else:
        secure = True
        print("---------------------")
        print("Switched to SECURE mode")
        print("---------------------")
    reset()

def setup():
    """Setup button, MCP and pot."""
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
    GPIO.add_event_detect(secure_btn, GPIO.FALLING, callback=secure_insecure_callback, bouncetime=300)

    reset()

def get_direction(start_voltage, end_voltage):
    if start_voltage > end_voltage:
        return "R"
    else:
        return "L"

def check_times(secure):
    global user_times, code_times
    if secure == False:
        user_times.sort()
        code_times.sort()
        #TODO: sort user times, code times
        pass
    for i in range(0, len(user_times)):
        if abs(user_times[i] - code_times[i]) > time_tolerance:
            return False 
    return True

def check_positions(secure):
    global user_directions, code_positions
    if secure == False:
        # insecure mode is not position dependent
        return True
        pass
    for i in range(0, len(user_directions)):
        if user_directions[i] != user_directions[i]:
            return False 
    return True

def main():
    global start, begin, end, secure
    setup()

    start_voltage = mcp.read_adc(pot_channel)
    end_voltage = mcp.read_adc(pot_channel)
    new_value = True

    while start:
        print("User times")
        print("-------------------------------------------------")
        print(user_times)
        print("User directions")
        print("-------------------------------------------------")
        print(user_directions)
        while abs(end_voltage - start_voltage) < pot_tolerance:
            # wait while pot is not moving
            end_voltage = mcp.read_adc(pot_channel)

            ### if pot input restart time
            end = timer()
            new_value = False
            time.sleep(0.3)
#            if (end-begin) > 2:
                # two seconds have elapsed, quit
                # start = False
                # break

        # start timer
        begin = timer()

        new_start = mcp.read_adc(pot_channel)
        new_end = mcp.read_adc(pot_channel)

        while abs(start_voltage-new_start) > pot_tolerance:
            # wait while pot is moving
            new_end = mcp.read_adc(pot_channel)
            new_value = True
            time.sleep(0.3)
            new_start = mcp.read_adc(pot_channel)
            if abs(new_end-new_start) < pot_tolerance:
                break
            
            #if (end-begin) > 1:
            #    break
    
        # end timer
        end = timer()
        if new_value:
            print("Start voltage: "+str(start_voltage))
            print("End voltage; "+str(new_start))
            user_times.append((end-begin)*1000)
            print(end-begin)
            user_directions.append(get_direction(start_voltage, end_voltage))
            new_value = False
            start_voltage = mcp.read_adc(pot_channel)
            end_voltage = mcp.read_adc(pot_channel)
        if (len(user_directions) == len(code_directions)) or len(user_directions) >= 16:
            break
    
    print("User times")
    print("-------------------------------------------------")
    print(user_times)
    print("User directions")
    print("-------------------------------------------------")
    print(user_directions)
    print("-------------------------------------------------")
    print("-------------------------------------------------")
    print("-------------------------------------------------")
    if (check_times(secure) and check_positions(secure)):
        print("Success biatch")
        GPIO.output(LED_unlock, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(LED_unlock, GPIO.LOW)
        #TODO play unlock
    else:
        print("Do better")
        GPIO.output(LED_lock, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(LED_lock, GPIO.LOW)
        #TODO play lock
        pass
    GPIO.cleanup()

if __name__ == "__main__":
    main()

