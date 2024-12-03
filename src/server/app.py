# Use Flask as web framework for web server
from flask import Flask, render_template, request
app = Flask(__name__)

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
            # TODO send signals out rpi gpio to start coffee making
            if "start" in request.form:
                return 'Starting coffee making!'
            elif "cancel" in request.form:
                return 'Cancelling brewing'
	return render_template('coffee.html')
# @app.route('/newpage')
# def newpage():
	# return 'Second page if needed'
	
# if __name__ == '__main__':
# app.run(debug = True, host = '0.0.0.0')

