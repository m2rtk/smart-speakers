
import RPi.GPIO as GPIO
import time
import sys
from collections import deque
from speaker_controller import SpeakerController

"""
This will try to decode the speakers 2-digit 7-segment led panel.
"""

lookup = [
    0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B, 0x00, 0x00, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47, 0x5E, 
    0x37, 0x06, 0x3C, 0x57, 0x0E, 0x55, 0x15, 0x1D, 0x67, 0x73, 0x05, 0x5B, 
    0x0F, 0x3E, 0x1C, 0x5C, 0x13, 0x3B, 0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 
    0x00, 0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47, 0x5E, 0x37, 0x06, 0x3C, 0x57, 
    0x0E, 0x55, 0x15, 0x1D, 0x67, 0x73, 0x05, 0x5B, 0x0F, 0x3E, 0x1C, 0x5C, 
    0x13, 0x3B, 0x6D
]

def decode(n):
    if n not in lookup:
        return ' '

    index = lookup.index(n)

    return chr(index + 48)

class Reading:
    def __init__(self, state):
        self.state = state

    def __init__(self, state):
        """todo figure out if this abstraction is worth it"""
        """
        The first 7 bits are data pins (A, B, C, D, E, F, G), 8th bit is left toggler, 9th bit is right toggle
        """
        self.state = state

    @property
    def string(self):
        return ''.join(map(str, self.state))

    @property
    def int(self):
        return int(self.string, 2)

    @property
    def translated(self):
        t = decode(self.data_int)

        l = t if self.state[7] else ' '
        r = t if self.state[8] else ' '

        return l + r

    @property
    def data_int(self):
        return int(self.string[:7], 2)

    def write(self, pins):
        for i in range(len(self.state)):
            GPIO.output(pins[i], self.state[i])

    def __repr__(self):
        return f"{self.string} {hex(self.data_int)} {self.translated}"

    def __eq__(self, other):
        return self.string.__eq__(other.string)

    def __hash__(self):
        return self.string.__hash__


class Display:
    def __init__(self, pins):
        self.pins = pins

    def read(self):
        state = []
        for pin in self.pins:
            i = pin.read()
            pin.write()
            state.append(i)
        reading = Reading(state)
        print(reading)
        return reading

    def write(self, reading):
        for i in range(9):
            pin = self.pins[i]
            value = reading.state[i]
            pin.write(value)


class DisplayPin:
    def __init__(self, name, in_pin, out_pin):
        self.name = name
        self.in_pin = in_pin
        self.out_pin = out_pin
        self.last_value = None

    def auto_sync(self):
        GPIO.add_event_detect(self.in_pin, GPIO.BOTH, callback = lambda ch: GPIO.output(self.out_pin, GPIO.input(self.in_pin)))

    def read(self):
        self.last_value = GPIO.input(self.in_pin)
        return self.last_value

    def write(self, value=None):
        if value is None and self.last_value is None:
            value = self.read()
        elif value is None:
            value = self.last_value

        GPIO.output(self.out_pin, value)

    def setup(self):
        GPIO.setup(self.in_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.out_pin, GPIO.OUT)

    def __repr__(self):
        return f"{self.name}(in={self.in_pin} out={self.out_pin})"


if __name__ == '__main__':
    args = sys.argv
    INTERVAL = 0.1
    INPUT_PINS = [14, 15, 8, 7, 1, 12, 16, 20, 21]
    OUTPUT_PINS = [11, 9, 10, 22, 27, 17, 4, 3, 2]
    CONTROLLER_PINS = [13, 19, 26]

    """
    The board pinout (goes towards backplate):
     --backplate-->
    G A F L D E C B R
    0 1 2 3 4 5 6 7 8
    """

    PINS = [
        DisplayPin('A', INPUT_PINS[1], OUTPUT_PINS[1]),
        DisplayPin('B', INPUT_PINS[7], OUTPUT_PINS[7]),
        DisplayPin('C', INPUT_PINS[6], OUTPUT_PINS[6]),
        DisplayPin('D', INPUT_PINS[4], OUTPUT_PINS[4]),
        DisplayPin('E', INPUT_PINS[5], OUTPUT_PINS[5]),
        DisplayPin('F', INPUT_PINS[2], OUTPUT_PINS[2]),
        DisplayPin('G', INPUT_PINS[0], OUTPUT_PINS[0]),
        DisplayPin('L', INPUT_PINS[3], OUTPUT_PINS[3]),
        DisplayPin('R', INPUT_PINS[8], OUTPUT_PINS[8])
    ]
    
    if len(args) == 10:
        print("todo argument support")
        exit(1)
    elif len(args) >= 2 and args[1] == 'default':
        if len(args) == 3:
            INTERVAL = int(args[2]) / 1000
    else:
        print("Expected 10 arguments: PIN0, PIN1, PIN2, PIN3, PIN4, PIN5, PIN6, PIN7, PIN8")
        exit(1)


    GPIO.setmode(GPIO.BCM) 
    GPIO.setwarnings(0)

    print(f"Using pins: {PINS}")
    for pin in PINS:
        pin.setup()
        pin.auto_sync()

    print(f"Using interval: {INTERVAL}")
    controller = SpeakerController(CONTROLLER_PINS[0], CONTROLLER_PINS[1], CONTROLLER_PINS[2])
    display = Display(PINS)
    while True:
        user_input = input("")

        if user_input.lower().startswith("w"):
            _, state = user_input.split(" ", 2)
            state = list(map(int, list(state)))
            reading = Reading(state)
            display.write(reading)
        elif user_input.lower().startswith("g"):
            _, duration, interval_ms = user_input.split(" ", 3)
            start = time.time()
            while True:
                if time.time() - start > int(duration):
                    break
                display.read()
                time.sleep(int(interval_ms) / 1000)
        elif user_input.lower().startswith("s"):
            _, command_name = user_input.split(" ", 2)
            controller.send(command_name)
            time.sleep(0.2)
            for i in range(10):
                display.read()
                time.sleep(INTERVAL)
        else:
            for i in range(10):
                display.read()
                time.sleep(INTERVAL)


        # time.sleep(INTERVAL)



