from flask import Flask, render_template, request

preset_time = None
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		# TODO send signals out rpi gpio to start coffee making
		return 'Starting coffee making!'
	return render_template('coffee.html', preset_time=preset_time)
# @app.route('/newpage')
# def newpage():
	# return 'Second page if needed'
if __name__ == '__main__':
	app.run(debug = True, host = '0.0.0.0')

