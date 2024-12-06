import serial, pigpio, time, traceback

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
        self.LCD.write(signal)
        self.LCD.flush()
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
if __name__ == "__main__":
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

