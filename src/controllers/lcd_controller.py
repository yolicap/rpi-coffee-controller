import serial, pigpio, time, traceback

class LCDController():

    INIT_STATUS = False

    LCD = None
    PI = None

    PIN_RX = None
    PIN_TX = None
    PIN_RS = None

    def __init__(self, pi, rx, tx, rs):
        self.PI = pi
        self.PIN_RX = rx
        self.PIN_TX = tx
        self.PIN_RS = rs

    def init(self):

        init_status = False

        # initiate serial on provided ports
        # self.PI.set_pull_up_down(self.PIN_RS, pigpio.PUD_DOWN)
        # self.PI.set_mode(self.PIN_RS, pigpio.OUTPUT)
        self.PI.set_mode(self.PIN_TX, pigpio.ALT5)
        self.PI.set_mode(self.PIN_RX, pigpio.ALT5)

        # import subprocess
        # result = subprocess.run(['ls', '/dev/'], stdout=subprocess.PIPE)
        # print(result.stdout)

        try:
            self.LCD = serial.Serial(
                port="/dev/ttyS0", 
                baudrate=9600, 
            )
            # self.LCD.open()

            # TODO init signal

            print("Successfully started LCD")
            init_status = True
        except IOError:
            print(traceback.format_exc())
            print("Could not initiate LCD")
            init_status = False

        # final
        self.INIT_STATUS = init_status

        # set baud
        # self.LCD.write(b'\x00\x0B\x01\x38')

        # resset and clear screen
        self.reset()
        self.clear()

        time.sleep(1)
        # set text configs
        self.LCD.write(b'\xFF\x7F\xFF\xFF') # initial text color, white
        time.sleep(1)
        # self.LCD.write(b'') # initial screen oreintation, portrait
        self.LCD.write(b'\xFF\x7D\x00\x07') # initial font FONT_7X8
        time.sleep(1)

        return init_status
    
    def write_signal(self, signal):
        response = None
        self.LCD.write(signal)
        self.LCD.flush()
        while not self.LCD.readable():
            time.sleep(0.01)
        if self.LCD.readable():
            # response = self.LCD.read(size=1)
            response = 0
        if response == b'\x06':
            print("ack recieved from LCD")
        else :
            # print("nack recieved : ", response)
            pass

        return response
    
    def reset(self):
        self.PI.write(self.PIN_RS, 0)
        time.sleep(0.5)
        self.PI.write(self.PIN_RS, 1)
        time.sleep(5)

        self.LCD.reset_output_buffer()
        print("reset lcd")

    def clear(self):
        self.write_signal(b'\xFF\xD7')
        print("cleared lcd")

    def message(self, msg: str):
        signal = b'\x00\x06'
        # signal += str.encode(msg[:255])
        signal += str.encode(msg)
        signal += b'\x00'

        self.write_signal(signal)

        print("sent string to LCD")

        # TODO : wait till sucess

    def brewing_message(self):
        self.message("brewing...")

    def keep_warm_message(self):
        self.message("keeping warm")

    def cleaning_message(self):
        self.message("clean me!")

    def ready_message(self):
        self.message("ready to brew")

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

