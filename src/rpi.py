import pigpio
import statemachine
from threading import *
import time

pi = pigpio.pi()
statemachine.start_machine()

# how will app communicate with rpi? web frameworks typically
# don't work within a thread. maybe open tcp connection?
# one thread for inputs and one thread for outputs?
# instead of constantly checking state, can set some kind of interrupt? or comm. socket?

# inputs
clean_button = 4
brew_button = 27
def input_handler():
	global clean_button
	global brew_button
	global pi

	while True:
		if pi.read(clean_button):
			statemachine.press_clean_button()
		if pi.read(brew_button):
			statemachine.press_brew_button()

# outputs
blue_led = 22
red_led = 23
def output_handler():
	global blue_led
	global red_led
	global pi

	while True:
		state = statemachine.get_state()
		if state == 0:
			pi.write(blue_led, 1)
			pi.write(red_led, 0)
			# TODO signal(s) for not brewing

		elif state == 1:
			pi.write(blue_led, not pi.read(blue_led))
			pi.write(red_led, 0)
			# there is probably a better way to do the blinking
			# but waiting 0.5 seconds should not be too much of a problem because
			# brewing for 0.5 too long or too short will not make much of a difference
			time.sleep(0.5)

			# TODO signal(s) for brewing
		elif state == 2:
			pi.write(red_led, 1)
			pi.write(blue_led, 0)
			# TODO signal(s) for not brewing

def start():
	input_process = Thread(target = input_handler)
	ouput_process = Thread(target = output_handler)
