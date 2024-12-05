# State Machine
# states: {0: idle (not brewing, clean), 1: brewing, 2: finished (not brewing, dirty)}
from threading import *
import datetime
import time

preset_time = None
timer = None
clean_button_pressed = False
brew_button_pressed = False

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

def press_clean_button():
	global clean_button_pressed
	clean_button_pressed = True

def press_brew_button():
	global brew_button_pressed
	brew_button_pressed = True

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
	global brew_button_pressed
	global clean_button_pressed
	while True:
		if state == 0:
			# manual brewing by button press
			if brew_button_pressed:
				state = 1
			# remote request to brew
			elif brew_request:
				state = 1
		elif state == 2:
			# filter cleaned button pressed
			if clean_button_pressed:
				state = 0
		elif state == 1:
			# TODO how to know when brewing is done?
			pass
		# TODO race conditions? what if button is pressed right before this?
		# assume press lasts longer than loop ?
		# if button is pressed in wrong state, remove press and do nothing
		brew_button_pressed = False
		clean_button_pressed = False
		brew_lock.acquire()
		brew_request = False
		brew_lock.release()
		# allow 0.2 seconds for user to press buttons
		time.sleep(0.2)


# start_machine()
