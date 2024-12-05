# Use Flask as web framework for web server
from flask import Flask, render_template, request
app = Flask(__name__)

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		print(request.form)
        	# TODO send signals out rpi gpio to start coffee making
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
	app.run(debug = True, host = '0.0.0.0')

