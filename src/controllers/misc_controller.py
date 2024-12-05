import pigpio

# pi = pigpio.pi()
# print("read: ", pi.read(4))
# print("write: ", pi.write(4, 1))

# handles raspberry pi inputs and outputs
class MiscController():
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

    def brew_button_pressed(self):
        return self.pi.read(self.brew_button)

    def clean_button_pressed(self):
        return self.pi.read(self.clean_button)

    def set_blue_led(self, value):
        self.pi.write(self.blue_led, value)

    def set_red_led(self, value):
        self.pi.write(self.red_led, value)

    def get_blue_led(self):
        return self.pi.read(self.blue_led)

