# State Machine
# states: {0: idle (not brewing, clean), 1: brewing, 2: finished (not brewing, dirty)}
from threading import *
import datetime
import time
import misc_controller

preset_time = None
timer = None

# Shared Variables
state = 0
state_lock = Lock()
# if the user has remotely sent a request to brew
brew_request = False
brew_lock = Lock()

# get difference in seconds from now until preset brewing time
# preset_time format: HH:MM
def get_delay():
	global preset_time
	preset_hour = preset_time[0:2]
	preset_min = preset_time[3:5]
	delay = 0

	# assume for now that datetime.now() gets the correct time in the correct zone
	curr_time = datetime.datetime.now().time()
	curr_hour = curr_time.hour
	curr_min = curr_time.minute
	curr_sec = curr_time.second

	# count remainder of seconds in current minute
	delay += (60 - curr_sec)
	curr_min += 1
	if curr_min >= 60:
		curr_hour += 1
		curr_min = 0

	# count remainder of minutes in current hour
	delay += (60 - curr_min) * 60
	curr_hour = (curr_hour + 1) % 24

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

# handle brewing at a set time
def time_brewing():
	global state
	global state_lock
	if state == 0:
		state_lock.acquire()
		state = 1
		state_lock.release()
		# restart timer
		set_time()

def set_time():
	global timer
	global preset_time
	if timer:
		timer.cancel()
	timer = Timer(get_delay(), time_brewing)
	timer.start()

def start_machine():
	global state
	global brew_request
	global brew_lock

	# initalize components
	pi = pigpio.pi()
	misc_ctrl = misc_controller.MiscController(pi, blue_led=22, red_led=27,
		brew_button=17, clean_button=23)


	while True:
		if state == 0:
			# SET OUTPUTS
			# can this be more efficient? constantly setting to the same value?
			misc_ctrl.set_blue_led(1)
			misc_ctrl.set_red_led(0)

			# HANDLE STATE TRANSITIONS
			# manual brewing by button press
			if misc_ctrl.brew_button_pressed():
				state = 1

			# remote request to brew
			elif brew_request:
				state = 1

		elif state == 1:
			# SET OUTPUTS
			misc_ctrl.set_blue_led(not misc_controller.get_blue_led())
			misc_ctrl.set_red_led(0)
			# there is probably a better way to do the blinking
			# but waiting 0.5 seconds should not be too much of a problem because
			# brewing for 0.5 too long or too short will not make much of a difference
			time.sleep(0.5)

			# HANDLE STATE TRANSITIONS
			# TODO how to know when brewing is done?
			pass

		elif state == 2:
			# SET OUTPUTS
			misc_ctrl.set_red_led(1)
			misc_ctrl.set_blue_led(0)

			# HANDLE STATE TRANSITIONS
			# filter cleaned button pressed
			if misc.ctrl.clean_button_pressed():
				state = 0

		brew_lock.acquire()
		brew_request = False
		brew_lock.release()

		# allow 0.2 seconds for user to press buttons
		time.sleep(0.2)


# start_machine()
