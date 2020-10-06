# importing the requests library
import json
import time
import requests

# api-endpoint
URL = "http://192.168.1.6/api/pWH0J9PLMzz5bRzy3wPgHfTOuUz2UKf3XNW13owt"

HEADERS = {"Content-Type": "application/json"}

# Json preformatting
on = {"on": True}
off = {"on": False}

# Remote codes
I_button = 1002
bright = 2002
dim = 3002
O_button = 4002

# Last button press
# TODO add function to check last timestamp at start
max_t = "2020-10-05T14:43:41"

# blinker values
wanted = 0
blinked = 0

# running
running = False
blinking = False
stopped = True

# timer values in secs
loop_speed = 2  # 1 was too fast for blinking
# TODO check if there is faster way (brightness?) to control blinking
on_delay = 120  # time from press to start
blink_interval = 1  # time between blinks
t = 0  # running timer
off_delay = 420  # from start to off?
counter_delay = 60  # blink every minute?
lastblink = 0  # counter at last blink starting


def switch(direction):
    """
    Switch light (on)/(off)
    """
    path = "/lights/1/state"
    requests.put(URL + path, data=json.dumps(direction), headers=HEADERS)
    return 1


def state():
    """
    Get state of light
    """
    path = "/lights/1"
    res = requests.get(URL + path)
    dictionary = res.json()
    # print(dictionary['state']['on'])
    if dictionary['state']['on']:
        return 1
    else:
        return 0


def last_stamp():
    """
    Gets the last stamp from the remote
    """
    path = "/sensors/2"
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
    path = "/sensors/2"
    res = requests.get(URL + path)
    dictionary = res.json()
    # print(dictionary['state'])
    last = dictionary['state']['buttonevent']
    timestamp = dictionary['state']['lastupdated']
    # print(last, timestamp)

    ### modify the timestamp to another format
    # tuple_time = time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    # GMTtime = time.strftime("%a, %d %b %Y %X GMT", tuple_time)
    # print("New", GMTtime)

    ### this is the previously saved last stamp
    # tuple_time = time.strptime(max_t, "%Y-%m-%dT%H:%M:%S")
    # GMTtime = time.strftime("%a, %d %b %Y %X GMT", tuple_time)
    # print("Record", GMTtime)

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


def change():
    """
    Get current status, and switch it
    """
    if state():
        switch(off)
    else:
        switch(on)


def blinks_wanted():
    """
    Check and save the amount of blinks wanted
    """
    global lastblink
    global wanted
    global blinking

    lastblink = t
    wanted = (int(t / 60)) * 2  # want to blink correct amount
    # on and off is 2
    blinking = True  # blink with the first press too
    print("Blink: ", wanted)
    print("Started")
    return 0


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

    # States
    global running
    global stopped
    global blinking

    # Counters
    global blinked
    global wanted

    t -= 1
    if stopped:
        # switch off at the start
        switch(off)
        if button_pressed():
            # set current to timer
            t = on_delay
            lastblink = on_delay
            print(t)
            stopped = False
            running = True
            blinks_wanted()  # sets counters and timers and blinking = true

    if blinking:
        if blinked < wanted:
            blinked += 1
            print("Blink: ", blinked)
            change()
        if blinked >= wanted:
            print("Blinking done ", t)
            blinked = 0
            blinking = False

    if running:
        # if last blink was 60s ago
        if (t + counter_delay) < lastblink:
            blinks_wanted()  # sets counters and timers and blinking = true
        if t <= 0:
            switch(on)
            running = False
            blinking = False
            stopped = True
            t = 0


# get last stamp first so we dont start immediately
# also works to find that the we have access to bridge?
print(max_t)
max_t = last_stamp()
print(max_t)

while 1:
    # control loop here
    control_loop()
    print(t)
    time.sleep(loop_speed)
