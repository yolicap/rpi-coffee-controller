import serial

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

        # TODO : what is the correct port?
        # initiate serial on provided ports
        try:
            self.LCD = serial.Serial(
                port=None, 
                baudrate=9600, 
            )
            self.LCD.open()

            # TODO init signal

            print("Successfully started LCD")
            init_status = True
        except IOError:
            print("Could not initiate LCD")
            init_status = False

        # final
        self.INIT_STATUS = init_status

        # set baud
        self.LCD.write(b'\x00\x0B\x01\x38')

        # resset and clear screen
        self.reset()
        self.clear()

        # set text configs
        self.LCD.write(b'\xFF\x7F\xFF\xFF') # initial text color, white
        # self.LCD.write(b'') # initial screen oreintation, portrait
        self.LCD.write(b'\xFF\x7D\x00\x07') # initial font FONT_7X8

        return init_status
    
    def write_signal(signal):
    #     while (!_cmd.readable()) wait_ms(TEMPO);              // wait for screen answer
    # if (_cmd.readable()) resp = _cmd.getc();           // read response if any
    # switch (resp) {
    #     case ACK :                                     // if OK return   1
    #         resp =  1;
    #         break;
    #     case NAK :                                     // if NOK return -1
    #         resp = -1;
    #         break;
    #     default :
    #         resp =  0;                                 // else return   0
    #         break;
    # }
        pass
    
    def reset(self):
        pass

    def clear(self):
        self.LCD.write(b'\xFF\xD7')

    def message(self, msg: str):
        signal = b'\x00\x66'
        signal += str.encode(str[:255])
        signal += b'\x00'

        self.LCD.write(signal)

        # TODO : wait till sucess

    def brewing_message(self):
        self.message("brewing...")

    def keep_warm_message(self):
        self.message("keeping warm")

    def cleaning_message(self):
        self.message("clean me!")

    def ready_message(self):
        self.message("ready to brew")