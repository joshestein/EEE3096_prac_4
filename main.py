import RPi.GPIO as GPIO
import Adafruit_MCP3008
import pygame
from timeit import default_timer as timer
import time

#---------------------------------- Constants ----------------------------------#

secure_btn = 23
start_stop_btn = 24
custom_code_btn = 22
LED_unlock = 2
LED_lock = 3

CLK = 11
MOSI = 10
MISO = 9
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

pot_channel = 0

#------------------------------ Global Variables -------------------------------#

pot_tolerance = 30
time_tolerance = 100 #very big for testing
start = False
secure = True
custom_code = False
code_length = 3
lock_status = "unlocked"

begin = 0.0
end = 0.0
user_times = []
user_directions = []

#---------------------------- Default code sequence ----------------------------#

code_times = [300, 300, 300] #in ms
code_directions = ["L", "L", "R"]

#---------------------------------- Functions ----------------------------------#

def clear():
    """Clear user entered data"""
    global begin, user_times, user_directions
    begin = timer()
    user_times = []
    user_directions = []

def reset():
    """Method to reset all variables to default values"""
    global start, secure, custom_code
    clear()
    start = False
    secure = True
    custom_code = False
    print("Resetting to SECURE mode")

def start_stop_callback(channel):
    """Method to activate start mode after button press"""
    global start 
    if start:
        start = False
    else:
        start = True
        print("---------------------")
        print("Starting")
        print("---------------------")
    clear()

def secure_insecure_callback(channel):
    """Method to toggle secure/insecure mode after button press."""
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
    clear()

def custom_code_callback(channel):
    """Method to set custom code after button press."""
    global custom_code, start, code_directions, code_times, code_length
    if custom_code == False:
        custom_code = True
        code_directions = []
        code_times = []
        code_length = input("Please enter the desired length of your code:\n")
        print("\nPlease enter your code")
        start = True
    else:
        custom_Code = False
    
def setup():
    """Setup button, MCP and pot."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(secure_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(start_stop_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(custom_code_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    GPIO.setup(LED_unlock, GPIO.OUT)
    GPIO.setup(LED_lock, GPIO.OUT)
    
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)

    GPIO.add_event_detect(start_stop_btn, GPIO.FALLING, callback=start_stop_callback, bouncetime=500)
    GPIO.add_event_detect(secure_btn, GPIO.FALLING, callback=secure_insecure_callback, bouncetime=300)
    GPIO.add_event_detect(custom_code_btn, GPIO.FALLING, callback=custom_code_callback, bouncetime=300)

    print("Starting in UNLOCKED state")
    reset()

def get_direction(start_voltage, end_voltage):
    """Method to get the direction based on change in voltage"""
    if start_voltage > end_voltage:
        return "R"
    else:
        return "L"

def check_times():
    """Method to compare user entered times and code times"""
    global user_times, code_times, secure
    if secure == False:
        user_times.sort()
        code_times.sort()
    for i in range(0, len(user_times)):
        if abs(user_times[i] - code_times[i]) > time_tolerance:
            return False 
    return True

def check_positions():
    """Method to compare user entered directions and code directions"""
    global user_directions, code_directions, secure
    if secure == False:
        # insecure mode is not position dependent
        return True
    for i in range(0, len(user_directions)):
        if user_directions[i] != code_directions[i]:
            return False 
    return True

def success():
    """Method to indicate lock status upon succeessfully entered code, and play corresponding sound"""
    global lock_status
    if pygame.mixer.get_init() == None:
        pygame.mixer.init()
    print("Success biatch")
    if lock_status == "unlocked":
        GPIO.output(LED_lock, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(LED_lock, GPIO.LOW)
        pygame.mixer.music.load("Lock.mp3")
        lock_status = "locked"
        print("****************************")
        print("Changed to a LOCKED state")
        print("****************************")
    else:
        GPIO.output(LED_unlock, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(LED_unlock, GPIO.LOW)
        pygame.mixer.music.load("Unlock.mp3")
        lock_status = "unlocked"
        print("****************************")
        print("Changed to an UNLOCKED state")
        print("****************************")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

def fail():
    """Method to indictae incorrectly entered code and play corresponding sound"""
    print("Do better")
    if pygame.mixer.get_init() == None:
        pygame.mixer.init()
    pygame.mixer.music.load("Wrong.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

#--------------------------------- Main --------------------------------#

def main():
    global start, begin, end, secure, code_length, custom_code
    setup()

    try:
        while True:
            start_voltage = mcp.read_adc(pot_channel)
            end_voltage = mcp.read_adc(pot_channel)
            new_value = True
            time.sleep(0.2)
            while start:
                begin = timer()
                #print("User times")
                #print("-------------------------------------------------")
                #print(user_times)
                #print("User directions")
                #print("-------------------------------------------------")
                #print(user_directions)
                timeout = False
                while abs(end_voltage - start_voltage) < pot_tolerance:
                    # wait while pot is not moving
                    end_voltage = mcp.read_adc(pot_channel)

                    ### if pot input restart time
                    end = timer()
                    if (end-begin) > 4:
                         # four seconds have elapsed, quit
                         timeout = True
                         break
                    new_value = False
                    time.sleep(0.3)

                if timeout:
                    clear()
                    print("Timeout")
                    start = False
                    break
                begin = timer() # end button

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
                    
                end = timer() # end timer
                if new_value:
                    if custom_code:
                        code_times.append((end-begin)*1000)
                        code_directions.append(get_direction(start_voltage, end_voltage))
                    else:
                        user_times.append((end-begin)*1000)
                        user_directions.append(get_direction(start_voltage, end_voltage))
                    new_value = False
                    
                    # reset voltages to new position
                    start_voltage = mcp.read_adc(pot_channel)
                    end_voltage = mcp.read_adc(pot_channel)
                if custom_code:
                    if len(code_times) == code_length:
                        print("Succesfully entered custom code")
                        print(code_times)
                        print(code_directions)
                        reset()
                        break
                else:
                    if (len(user_directions) == len(code_directions)) or len(user_directions) >= 16:
                        print("User times")
                        print("-------------------------------------------------")
                        print(user_times)
                        print("User directions")
                        print("-------------------------------------------------")
                        print(user_directions)
                        print("-------------------------------------------------")
                        if (check_times() and check_positions()):
                            success()
                        else:
                            fail()
                        clear()
                        start = False
                        break
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()

