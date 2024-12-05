import statemachine
from threading import *

def state_machine_handler():
	sm = statemachine.StateMachine()
	sm.start_machine()

# Use Flask as web framework for web server
from flask import Flask, render_template, request
app = Flask(__name__)

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		# print(request.form)
		if "start" in request.form:
			return 'Starting coffee making!'
		elif "cancel" in request.form:
			return 'Cancelling brewing'
		elif "submit-brew-time" in request.form:
			return 'Brewing time set to ' + request.form['time']
	return render_template('coffee.html')
# @app.route('/newpage')
# def newpage():
	# return 'Second page if needed'

if __name__ == '__main__':
	state_machine_process = Thread(target = state_machine_handler)
	state_machine_process.start()
	app.run(debug = True, host = '0.0.0.0')