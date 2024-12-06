import pigpio, threading, time

# Objectifies brewer pheripherals
class BrewerController():

    BREWING = False

    PI = None

    PIN_THERMO = None

    # might be required to be a PWM signal in the future.
    # keep as digital for PoC
    PIN_HEAT = None 
    PIN_BUZZ = None

    # inputs:
    #   pi - pigpio instance
    #   thermo - gpio pin number for thermostat
    #   heat - gpio pin number for heater
    #   buzzer - gpio pin number for buzzer
    def __init__(self, pi, thermo, heat, buzzer):
        self.PI = pi
        self.PIN_THERMO = thermo
        self.PIN_HEAT = heat
        self.PIN_BUZZ = buzzer

        # set pull up / down
        # self.PI.set_pull_up_down(self.PIN_THERMO, pigpio.PUD_OFF) # not permitted. keep commented
        # self.PI.set_pull_up_down(self.PIN_HEAT, pigpio.PUD_DOWN) # not permitted. keep commented
        # self.PI.set_pull_up_down(self.PIN_BUZZ, pigpio.PUD_DOWN) # not permitted. keep commented

        # set mode 
        # self.PI.set_mode(self.PIN_THERMO, pigpio.INPUT) # not permitted. keep commented
        # self.PI.set_mode(self.PIN_HEAT, pigpio.OUTPUT) # not permitted. keep commented
        # self.PI.set_mode(self.PIN_BUZZ, pigpio.OUTPUT) # not permitted. keep commented

        # set initial values
        self.PI.write(self.PIN_HEAT, 0)
        self.PI.write(self.PIN_BUZZ, 0)

    # Called from state machine.
    # If brew time (in minutes) is set, interrupt timer with be set and call stop_brew
    # Otherwise, turn off with thermostat values
    # Returns timer when time is passed, otherwise returns None.
    def brew(self, brew_time = None):
        timer = None
        self.BREWING = True

        # set IO interrupt
        if brew_time == None:
            # TODO : Currently no thermostat data. keep for future implementation
            pass
        # set timer interrupt
        else :
            timer = threading.Timer(brew_time, self.stop_brew)
            timer.start()

        # set output to high
        self.PI.write(self.PIN_HEAT, 1)

        # return timer so caller can cancel if brewing is stopped early
        return timer
    
    # Called from state machine or by timer interrupt
    # Stops brewing 
    def stop_brew(self):
        # turn off heat
        self.PI.write(self.PIN_HEAT, 0)
        self.buzzer()
        self.BREWING = False

    # set buzzer to high for a second
    def buzzer(self):
        self.PI.write(self.PIN_BUZZ, 1)
        time.sleep(1.0) 
        self.PI.write(self.PIN_BUZZ, 0)

    def is_brewing(self):
        return self.BREWING
