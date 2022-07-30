
import RPi.GPIO as GPIO
import time
import sys

"""
OUT_PIN is the pin (data pin on the speaker) we are going to send the IR commands to the speaker on. 

IN_PIN1 and IN_PIN2 are the gnd and 5v from the speaker. We don't make use of these but if these
pins are not connected to the pi then IR commands will be ignored. I am not an expert but I think
there needs to be a closed loop between the data pin and the gnd/5v pins.
"""

CYCLE_TIME = 0.0005
COMMANDS = {
    'VOLUME_UP' :   [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1],
    'VOLUME_DOWN' : [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1],
    'MUTE' :        [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1],
    'BASS_UP' :     [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
    'BASS_DOWN' :   [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
    'TREB_UP' :     [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
    'TREB_DOWN' :   [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1],
    'INPUT' :       [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1],
    'STANDBY' :     [18, 9, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1]
}


class SpeakerController:
    def __init__(self, out_pin, in_pin0, in_pin1):
        self.out_pin = out_pin

        GPIO.setmode(GPIO.BCM) 
        GPIO.setwarnings(0)
        GPIO.setup(out_pin, GPIO.OUT)
        #GPIO.setup(in_pin0, GPIO.IN)
        #GPIO.setup(in_pin1, GPIO.IN)

    def send(self, command):
        if isinstance(command, str):
            command = COMMANDS[command.upper()]

        current_state = True

        GPIO.output(self.out_pin, True)

        for duration in command:
            current_state = not current_state
            GPIO.output(self.out_pin, current_state)
            time.sleep(duration * CYCLE_TIME)

        GPIO.output(self.out_pin, True)



if __name__ == '__main__':
    args = sys.argv

    if len(args) == 2 and args[1] == 'default':
        OUT_PIN = 13
        IN_PIN0 = 19
        IN_PIN1 = 26
    elif len(args) == 4:
        OUT_PIN = int(args[1]) # 13
        IN_PIN0 = int(args[2]) # 19
        IN_PIN1 = int(args[3]) # 26
    else:
        print("Expected 3 arguments: OUTPUT_PIN, SOME_RANDOM_GPIO_PIN_0, SOME_RANDOM_GPIO_PIN_1")
        exit(1)

    controller = SpeakerController(OUT_PIN, IN_PIN0, IN_PIN1)

    print(f"Available commands: {', '.join(COMMANDS.keys())}, HELP, EXIT")
    while True:
        user_input = input("cmd>")

        if user_input.startswith("repeat"):
            _, command_name, times, delay_ms = user_input.split(' ', 4)
            print(command_name, times, int(delay_ms) / 1000)
            for i in range(int(times)):
                controller.send(command_name)
                time.sleep(int(delay_ms) / 1000)
        elif user_input.upper() == 'EXIT':
            exit(0)
        elif user_input.upper() == 'HELP':
            print(f"Available commands: {', '.join(COMMANDS.keys())}, HELP, EXIT")
        elif user_input.upper() in COMMANDS:
            command_name = user_input
            controller.send(command_name)




