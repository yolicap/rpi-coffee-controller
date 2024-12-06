# State Machine
# states: {0: idle (not brewing, clean), 1: brewing, 2: finished (not brewing, dirty)}
from threading import *
import datetime
import pigpio
import time
import os
import sys
child = os.path.abspath(os.path.join(os.path.dirname(__file__), 'controllers'))
sys.path.append(child)
import misc_controller

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

		# assume for now that datetime.now() gets the correct time in the correct zone
		curr_time = datetime.datetime.now().time()
		print("current time: ", curr_time)
		curr_hour = (int(curr_time.hour) - 5) % 24
		curr_min = int(curr_time.minute)
		curr_sec = int(curr_time.second)

		# count remainder of seconds in current minute
		# assume user will not set time within the same minute
		delay += (60 - curr_sec)
		curr_min += 1
		if curr_min >= 60:
			curr_hour += 1
			curr_min = 0
		print("delay after seconds: ", delay)

		# count remainder of minutes in current hour
		if curr_hour != preset_hour or (curr_hour == int(preset_hour) and int(preset_min) < curr_min):
			delay += (60 - curr_min) * 60
			curr_hour = (curr_hour + 1) % 24
		else:
			# count difference in minutes
			delay += (int(preset_min) - curr_min) * 60
			return delay
		print("delay after ", 60 - curr_min, " minutes: ", delay)

		# count difference in hours
		hour_diff = 0
		if (curr_hour > int(preset_hour)):
			hour_diff = int(preset_hour) + (24 - curr_hour)
		else:
			hour_diff = int(preset_hour) - curr_hour
		delay += hour_diff * 60 * 60
		print("delay after hour: ", delay)

		# count minutes in preset time
		delay += int(preset_min) * 60
		print("got delay of ", delay, " seconds")
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

	def start_machine(self):
		print("starting state machine. initializing components")
		# initalize components
		pi = pigpio.pi()
		misc_ctrl = misc_controller.MiscController(pi, blue_led=22, red_led=27,
			brew_button=17, clean_button=23)

		while True:
			if self.state == 0:
				# SET OUTPUTS
				# can this be more efficient? constantly setting to the same value?
				misc_ctrl.set_blue_led(1)
				misc_ctrl.set_red_led(0)

				# HANDLE STATE TRANSITIONS
				# manual brewing by button press
				if misc_ctrl.brew_button_pressed():
					print("in brew state from button press")
					self.state = 1

				# remote request to brew
				elif self.brew_request:
					print("in brewing state from brew request")
					self.state = 1
					self.brew_request = False
				elif self.timer_done:
					print("in brewing state from timer done")
					self.state = 1
					self.timer_done = False
				else:
					# if input sent in wrong state, clear flags
					self.cancel_request = False

			elif self.state == 1:
				# SET OUTPUTS
				misc_ctrl.set_blue_led(not misc_ctrl.get_blue_led())
				misc_ctrl.set_red_led(0)
				# there is probably a better way to do the blinking
				# but waiting 0.5 seconds should not be too much of a problem because
				# brewing for 0.5 too long or too short will not make much of a difference
				time.sleep(0.5)

				# HANDLE STATE TRANSITIONS
				# TODO how to know when brewing is done?
				if self.cancel_request:
					print("in dirty state from cancel")
					self.state = 2
				else:
					self.brew_request = False
					self.timer_done = False

			elif self.state == 2:
				# SET OUTPUTS
				misc_ctrl.set_red_led(1)
				misc_ctrl.set_blue_led(0)

				# HANDLE STATE TRANSITIONS
				# filter cleaned button pressed
				if misc_ctrl.clean_button_pressed():
					self.state = 0
				else:
					self.timer_done = False
					self.brew_request = False
					self.cancel_request = False

			# allow 0.2 seconds for user to press buttons
			time.sleep(0.2)
