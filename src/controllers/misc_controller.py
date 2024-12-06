import pigpio
from threading import *

# pi = pigpio.pi()
# print("read: ", pi.read(4))
# print("write: ", pi.write(4, 1))

# handles raspberry pi inputs and outputs
class MiscController():
    blinking_process = None
    blinking_active = False

    # outputs
    blue_led = None
    red_led = None

    #inputs
    brew_button = None
    clean_button = None

    pi = None

    def __init__(self, pi, blue_led, red_led, brew_button, clean_button):
        self.blue_led = blue_led
        self.red_led = red_led
        self.brew_button = brew_button
        self.clean_button = clean_button
        self.pi = pi
        self.blinking_process = Thread(target = self.blink_handler)

    def brew_button_pressed(self):
        return self.pi.read(self.brew_button)

    def clean_button_pressed(self):
        return self.pi.read(self.clean_button)

    def set_blue_led(self):
        self.pi.write(self.blue_led, 1)
        self.pi.write(self.red_led, 0)

    def set_red_led(self):
        self.pi.write(self.red_led, 1)
        self.pi.write(self.blue_led, 0)

    def blink_leds(self):
        self.blinking_active = True
        self.blinking_process.start()

    def stop_blinking(self):
        self.blinking_active = False
        self.blinking_process.join()

    def blink_handler(self):
        while self.blinking_active:
            self.pi.write(self.blue_led, not self.pi.read(self.blue_led))
            self.pi.write(self.red_led, 0)
        # end thread
