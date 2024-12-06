# State Machine
# states: {0: idle (not brewing, clean), 1: brewing, 2: finished (not brewing, dirty)}
from threading import *
import datetime
import pigpio
import serial, traceback
import time
import os
import sys
child = os.path.abspath(os.path.join(os.path.dirname(__file__), 'controllers'))
sys.path.append(child)
import brewer_controller
import misc_controller
# import lcd_controller

class StateMachine():
    preset_time = None
    timer = None
    timer_done = False

    state = 0
    # if the user has remotely sent a request to brew
    brew_request = False
    cancel_request = False

    def __init__(self):
        pass

    # get difference in seconds from now until preset brewing time
    # preset_time format: HH:MM
    def get_delay(self):
        print("preset time: ", self.preset_time)
        preset_hour = int(self.preset_time[0:2])
        preset_min = int(self.preset_time[3:5])
        delay = 0

        curr_time = datetime.datetime.now().time()
        # EST is 5 hours behind this clock
        curr_hour = (int(curr_time.hour) - 5) % 24
        print("current time: ", curr_time)
        curr_min = int(curr_time.minute)
        curr_sec = int(curr_time.second)

        # count remainder of seconds in current minute
        # assume user will not set time within the same minute
        delay += (60 - curr_sec)
        curr_min += 1
        if curr_min >= 60:
            curr_hour += 1
            curr_min = 0

        # count remainder of minutes in current hour
        if curr_hour != preset_hour or (curr_hour == int(preset_hour) and int(preset_min) < curr_min):
            delay += (60 - curr_min) * 60
            curr_hour = (curr_hour + 1) % 24
        else:
            # count difference in minutes
            delay += (int(preset_min) - curr_min) * 60
            return delay

        # count difference in hours
        hour_diff = 0
        if (curr_hour > int(preset_hour)):
            hour_diff = int(preset_hour) + (24 - curr_hour)
        else:
            hour_diff = int(preset_hour) - curr_hour
        delay += hour_diff * 60 * 60

        # count minutes in preset time
        delay += int(preset_min) * 60
        return delay

    # function to run when timer ends. handle brew at a set time
    def time_brewing(self):
        self.timer_done = True
        # restart timer
        self.set_time(self.preset_time)

    def set_time(self, preset_time):
        self.preset_time = preset_time
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.get_delay(), function=self.time_brewing)
        self.timer.start()

    def set_brew_request(self):
        self.brew_request = True

    def set_cancel_request(self):
        self.cancel_request = True

    def test_lcd(self):
        pi = pigpio.pi()
        lcd_controller = LCDController(pi, 14, 15, 16)
        lcd_controller.init()
        time.sleep(5)
        lcd_controller.message("hello world!")
        time.sleep(5)
        lcd_controller.write_signal(b'\xFF\xD7')
        lcd_controller.write_signal(b'\x00\x06\x48\x65\x6C\x6C\x6F\x00')
        time.sleep(3)
        lcd_controller.clear()
        time.sleep(3)
        while True:
            lcd_controller.ready_message()
            time.sleep(1)

    def start_machine(self):
        print("starting state machine. initializing components")
        # initalize components
        pi = pigpio.pi()
        # GPIO numbers
        blue_led = 22
        green_led = 5
        red_led = 27
        brew_button = 17
        clean_button = 23
        thermo = 26
        heat = 24
        buzzer = 25
        rx = 14
        tx = 15
        reset = 16
        # controllers
        misc_ctrl = misc_controller.MiscController(pi, red_led, green_led, blue_led,
            brew_button, clean_button)
        brew_ctrl = brewer_controller.BrewerController(pi, thermo, heat, buzzer)
        lcd_ctrl = LCDController(pi, rx, tx, reset)
        # lcd_controller.testing()
        print("lcd init : ", lcd_ctrl.init())
        print("lcd controller's LCD: ", lcd_ctrl.LCD)
        time.sleep(10)
        lcd_ctrl.write_signal(b'\xFF\xD7')
        lcd_ctrl.write_signal(b'\x00\x06\x48\x65\x6C\x6C\x6F\x00')
        print("rx mode: ", pi.get_mode(rx))
        print("tx mode: ", pi.get_mode(tx))

        lcd_ctrl.ready_message()
        time.sleep(0.5)
        print("sent ready message before loop")

        while True:
            if self.state == 0:
                # SET OUTPUTS
                # can this be more efficient? constantly setting even though already set?
                lcd_ctrl.ready_message()
                time.sleep(0.5)
                misc_ctrl.set_green_led()

                # HANDLE STATE TRANSITIONS
                # manual brewing by button press
                if misc_ctrl.brew_button_pressed():
                    print("in brew state from button press")
                    self.state = 1
                    # start brewing
                    brew_ctrl.brew(5)
                    # misc_ctrl.blink_leds()

                # remote request to brew
                elif self.brew_request:
                    print("in brewing state from brew request")
                    self.state = 1
                    self.brew_request = False
                    # start brewing
                    brew_ctrl.brew(5)
                    # misc_ctrl.blink_leds()
                # brewing at set time
                elif self.timer_done:
                    print("in brewing state from timer done")
                    self.state = 1
                    self.timer_done = False
                    # start brewing
                    brew_ctrl.brew(5)
                    # misc_ctrl.blink_leds()
                else:
                    # if input sent in wrong state, clear flags
                    self.cancel_request = False

            elif self.state == 1:
                lcd_ctrl.brewing_message()
                time.sleep(0.5)
                misc_ctrl.set_blue_led()
                if brew_ctrl.is_brewing():
                    if self.cancel_request:
                        print("in dirty state from cancel")
                        brew_ctrl.stop_brew()
                        # misc_ctrl.stop_blinking()
                        self.cancel_request = False
                        self.state = 2
                else: # the timer has run out and stopped brewing
                    self.state = 2

                # clear flags
                self.brew_request = False
                self.timer_done = False

            elif self.state == 2:
                lcd_ctrl.cleaning_message()
                time.sleep(0.5)
                # SET OUTPUTS
                misc_ctrl.set_red_led()

                # HANDLE STATE TRANSITIONS
                # filter cleaned button pressed
                if misc_ctrl.clean_button_pressed():
                    print("got clean button pressed")
                    self.state = 0
                else:
                    self.timer_done = False
                    self.brew_request = False
                    self.cancel_request = False

            # allow seconds for user to press buttons
            time.sleep(0.5)

# Objectifies LCD
class LCDController():

    INIT_STATUS = False

    LCD = None
    PI = None

    PIN_RX = None
    PIN_TX = None
    PIN_RS = None

    # Inputs:
    #   pi - pigpio instance
    #   rx - rx gpio pin on pi
    #   tx - tx gpio pin on pi
    #   rs - reset gpio pin on pi
    def __init__(self, pi, rx, tx, rs):
        self.PI = pi
        self.PIN_RX = rx
        self.PIN_TX = tx
        self.PIN_RS = rs

    # starts serial connection with LCD
    def init(self):

        init_status = False

        # initiate serial on provided ports
        # self.PI.set_pull_up_down(self.PIN_RS, pigpio.PUD_DOWN) # not permitted. keep commented
        # self.PI.set_mode(self.PIN_RS, pigpio.OUTPUT) # not permitted. keep commented
        self.PI.set_mode(self.PIN_TX, pigpio.ALT5) # ALT5 allows UART comm on /dev/ttyS0
        self.PI.set_mode(self.PIN_RX, pigpio.ALT5) # ALT5 allows UART comm on /dev/ttyS0

        # attempt to open connection on /dev/ttyS0
        try:
            self.LCD = serial.Serial(
                port="/dev/ttyS0",      # port
                baudrate=9600,          # default baud rate
            )

            print("Successfully started LCD")
            init_status = True

        # when connectin fails
        except IOError:
            print(traceback.format_exc())
            print("Could not initiate LCD")
            init_status = False

        # final
        self.INIT_STATUS = init_status

        # set baud
        # self.LCD.write(b'\x00\x0B\x01\x38') # not required. but keep commented pls :)

        # reset and clear screen
        self.reset()
        self.clear()
        time.sleep(1)

        # we're not really doing these but keep commented oops
        # set text configs
        # self.LCD.write(b'\xFF\x7F\xFF\xFF') # initial text color, white
        # self.LCD.write(b'') # initial screen oreintation, portrait

        self.LCD.write(b'\xFF\x7D\x00\x07') # initial font FONT_7X8
        time.sleep(1)

        return init_status
    
    # this writes signal but with extra steps...
    # ... those extra steps are flushing the output buffer and waiting .. just in case
    def write_signal(self, signal):
        response = None
        self.LCD.flush()

        # self.LCD.write(signal.pop(0))
        # self.LCD.write(signal.pop(0))
        for byte in signal:
            self.LCD.write(byte)
            time.wait(0.0005)
            
		# for (i = 0; i < number; i++) writeBYTE(command[i]);
        # 	_cmd.putc(c);
		# 	wait_ms(1);

        # self.LCD.write(signal)
        # self.LCD.flush()
        

        while not self.LCD.readable():
            time.sleep(0.01)

        # TODO : sometimes this gives us an error but we dont have time to fix that rn. keep commented :(
        if self.LCD.readable():
            # response = self.LCD.read(size=1)
            response = 0
        if response == b'\x06':
            print("ack recieved from LCD")
        else :
            # print("nack recieved : ", response)
            pass

        return response
    
    # pull down reset pin and wait 5 seconds just in case
    def reset(self):
        self.PI.write(self.PIN_RS, 0)
        time.sleep(0.5)
        self.PI.write(self.PIN_RS, 1)
        time.sleep(5)

        self.LCD.reset_output_buffer()
        print("reset lcd")

    # send clear command
    def clear(self):
        self.write_signal(b'\xFF\xD7')
        print("cleared lcd")

    # encode and send string
    def message(self, msg: str):
        signal = b'\x00\x06'
        # signal += str.encode(msg[:255])
        signal += str.encode(msg)
        signal += b'\x00'

        self.write_signal(signal)

        print("sent string to LCD")

    # predefined messages for your convinience 

    def brewing_message(self):
        self.clear()
        self.message("brewing...")
        time.sleep(0.5)

    def keep_warm_message(self):
        self.clear()
        self.message("keeping warm")
        time.sleep(0.5)

    def cleaning_message(self):
        self.clear()
        self.message("clean me!")
        time.sleep(0.5)

    def ready_message(self):
        self.clear()
        self.message("ready to brew")
        time.sleep(0.5)

# used for testing. ignore but keep for future testing
# if __name__ == "__main__":
def testing():
   # use arguments as ionput for message
    pi = pigpio.pi()
    lcd_controller = LCDController(pi, 14, 15, 16)
    lcd_controller.init()
    time.sleep(5)
    lcd_controller.message("hello world!")
    time.sleep(5)
    lcd_controller.write_signal(b'\xFF\xD7')
    lcd_controller.write_signal(b'\x00\x06\x48\x65\x6C\x6C\x6F\x00')
    time.sleep(3)
    lcd_controller.clear()
    time.sleep(3)
    while True:
        lcd_controller.ready_message()
        time.sleep(1)

