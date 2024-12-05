import pigpio, threading, time

class BrewerController():

    BREWING = False

    PI = None

    PIN_THERMO = None
    PIN_HEAT = None # TODO : should this be a pwm or high signal
    PIN_BUZZ = None

    # TODO : pass Pi
    def __init__(self, pi, thermo, heat, buzzer):
        self.PI = pi
        self.PIN_THERMO = thermo
        self.PIN_HEAT = heat
        self.PIN_BUZZ = buzzer

        # set pull up / down
        self.PI.set_pull_up_down(self.PIN_THERMO, pigpio.PUD_OFF)
        self.PI.set_pull_up_down(self.PIN_HEAT, pigpio.PUD_DOWN)
        self.PI.set_pull_up_down(self.PIN_BUZZ, pigpio.PUD_DOWN)

        # set mode 
        self.PI.set_mode(self.PIN_THERMO, pigpio.INPUT)
        self.PI.set_mode(self.PIN_HEAT, pigpio.OUTPUT)
        self.PI.set_mode(self.PIN_BUZZ, pigpio.OUTPUT)

        # set initial values
        self.PI.write(self.PIN_HEAT, 0)
        self.PI.write(self.PIN_BUZZ, 0)

    # Called from state machine.
    # If brew time (in minutes) is set, interrupt timer with be set and call stop_brew
    # Otherwise, turn with thermostat
    # returns timer when time is passed, otherwise returns None
    # TODO finished action: set timer or IO condition to call stop brew
    def brew(self, brew_time = None):
        timer = None
        self.BREWING = True

        # set IO interrupt
        if brew_time != None:
            # TODO
            pass
        # set timer interrupt
        else :
            timer = threading.Timer(brew_time, self.stop_brew)
            timer.start()

        # set output to high
        self.PI.write(self.PIN_HEAT, 1)

        return timer
    
    # Called from state machine.
    # Stops brewing 
    def stop_brew(self):
        # turn off heat
        self.PI.write(self.PIN_HEAT, 0)
        self.buzzer()
        BREWING = False

    # set buzzer to high for a second
    def buzzer(self):
        self.PI.write(self.PIN_BUZZER, 1)
        time.sleep(1.0) # TODO : non blocking 
        self.PI.write(self.PIN_BUZZER, 0)

    def is_brewing(self):
        return self.BREWING