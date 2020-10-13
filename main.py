# importing the requests library
import json
import time
import requests

# api-endpoint
URL = "http://192.168.1.6/api/pWH0J9PLMzz5bRzy3wPgHfTOuUz2UKf3XNW13owt"

LIGHT_GET = "/lights/1"
LIGHT_PUT = "/lights/1/state"
REMOTE_GET = "/sensors/2"

HEADERS = {"Content-Type": "application/json"}

# Json preformatting
on = {"on": True}
off = {"on": False}
alert = {"alert": "select"}

# Remote codes
I_button = 1002
bright = 2002
dim = 3002
O_button = 4002

# Last button press
max_t = 0

# blinker values
wanted = 0
blinked = 0
loops = 0
counter_step = 60 #once per x seconds? so 60 gives blink per remaining minutes

# running
running = False
blinking = False
stopped = True
lighted = False

# timer values in secs
loop_speed = 1  # 0.2 was too fast for blinking
on_delay = 300  # time from buttonpress to light on
t = 0  # running timer
off_delay = 120  # from start to off?
counter_delay = 60  # blink every minute?

def switch(direction):
    """
    Switch light (on)/(off)
    """
    path = LIGHT_PUT
    requests.put(URL + path, data=json.dumps(direction), headers=HEADERS)
    return 1


def state():
    """
    Get state of light
    """
    path = LIGHT_GET
    res = requests.get(URL + path)
    dictionary = res.json()
    if dictionary['state']['on']:
        return 1
    else:
        return 0


def last_stamp():
    """
    Gets the last stamp from the remote
    """
    path = REMOTE_GET
    res = requests.get(URL + path)
    sensor = res.json()
    stamp = sensor['state']['lastupdated']
    return stamp


def button_pressed():
    """
    Detect button presses
    Save time of latest press, and compare to that
    """
    global max_t
    path = REMOTE_GET
    res = requests.get(URL + path)
    dictionary = res.json()
    last = dictionary['state']['buttonevent']
    timestamp = dictionary['state']['lastupdated']

    if timestamp > max_t:
        max_t = timestamp
        print("Newer")
        if last == I_button:
            print("On")
            return 1
        if last == bright:
            return 0
        if last == dim:
            return 0
        if last == O_button:
            return 0
        else:
            print("Failed")
            return 0
    else:
        # print("Same or older")
        return 0

def flash():
    """
    Inbuilt flashing ability
    """
    path = "/lights/1/state"
    requests.put(URL + path, data=json.dumps(alert), headers=HEADERS)
    return 1


def blinks_wanted():
    """
    Check and save the amount of blinks wanted
    """
    global lastblink
    global wanted
    global blinking

    lastblink = t
    print(t)
    wanted = int((1 + t) / counter_step)  # want to blink correct amount (once for minute)
    blinking = True  # blink with the first press too
    print("Wanted: ", wanted)
    print("Started")
    return 1


def control_loop():
    """
    Here the program looks at the user inputs and controls lights accordingly
    """
    # Timers
    global on_delay
    global t
    global off_delay
    global counter_delay
    global lastblink
    global loops

    # States
    global running
    global stopped
    global blinking
    global lighted

    # Counters
    global blinked
    global wanted

    t -= 1

    if button_pressed():
        # set current to timer
        t = on_delay
        lastblink = on_delay
        print(t)
        stopped = False
        running = True
        lighted = False
        loops = 0 #reset loops
        blinks_wanted()  # sets counters and timers and blinking = true

    if stopped:
        t = 0

    if blinking:
        if blinked < wanted:
            blinked += 1
            print("Blink: ", blinked)
            flash()
        if blinked >= wanted:
            print("Blinking done ", t)
            blinked = 0
            blinking = False

    if running:
        if t <= 0:
            switch(on)
            running = False
            blinking = False
            stopped = False
            lighted = True
        # if last blink was 60s ago
        if (t <= on_delay - (loops * counter_delay)) & (t > 0):
            loops += 1
            blinks_wanted()  # sets counters and timers and blinking = true


    if lighted:
        #if light is on 60sec?
        #stay on for off_delay
        if t <= -off_delay:
            switch(off)
            running = False
            blinking = False
            stopped = True
            lighted = False


# get last stamp first so we dont start immediately
# also works to find that the we have access to bridge?
print(max_t)
max_t = last_stamp()
print(max_t)

#also switch off before loop?
switch(off)

while 1:
    # control loop here
    control_loop()
    print(t)
    time.sleep(loop_speed)
