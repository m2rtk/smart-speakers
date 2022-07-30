
import RPi.GPIO as GPIO
import time
import sys

"""
Syncs output of a pin to an input of another pin.
Can take in multiple such pairs.

The pins I used at the time of writing this script.
INPUT_PINS =  [14, 15,  8,  7,  1, 12, 16, 20, 21]
OUTPUT_PINS = [11,  9, 10, 22, 27, 17,  4,  3,  2]
"""

class PinPair:
    """
    This class is needed because the callback variable stuff is confusing. 
    local variables are not final or something like that so just sync(input_pin, output_pin) did not work
    """
    def __init__(self, input_pin, output_pin):
        self.input_pin = input_pin
        self.output_pin = output_pin

        GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(output_pin, GPIO.OUT)

    def setup_sync(self):
        def sync(ch):
            GPIO.output(self.output_pin, GPIO.input(self.input_pin))


        #GPIO.add_event_detect(self.input_pin, GPIO.BOTH, callback = lambda ch: GPIO.output(self.output_pin, GPIO.input(self.input_pin)))
        GPIO.add_event_detect(self.input_pin, GPIO.BOTH, callback = sync)
        print(f"Added sync from {self.input_pin:2d} to {self.output_pin:2d}")


if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)

    pairs = []

    for raw_pin_pair in sys.argv[1:]:
        input_pin, output_pin = map(int, raw_pin_pair.split('-', 2))
        pairs.append(PinPair(input_pin, output_pin))

    if len(pairs) == 0:
        print("No pairs given")
        exit(1)

    for pair in pairs:
        pair.setup_sync()

    while True:
        # add_event_detect has a happy little background thread doing all the actual work
        time.sleep(999)




