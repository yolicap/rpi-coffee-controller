from threading import *
import os
import sys
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent = os.path.abspath(os.path.join(curr_dir, ".."))
sys.path.append(parent)
# parent = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
# sys.path.append(parent)
import statemachine

sm = None

def state_machine_handler():
    global sm
    if not sm:
        sm = statemachine.StateMachine()
        print("starting state machine in app.py")
        sm.start_machine()
    else:
        print("state machine already initialized")

# Use Flask as web framework for web server
from flask import Flask, render_template, request
app = Flask(__name__)

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():
    global sm
    if request.method == 'POST':
        # print(request.form)
        if "start" in request.form:
            sm.set_brew_request()
            return 'Starting coffee making!'
        elif "cancel" in request.form:
            sm.set_cancel_request()
            return 'Cancelling brewing'
        elif "submit-brew-time" in request.form:
            print(request.form['time'])
            print(type(request.form['time']))
            sm.set_time(request.form['time'])
            return 'Brewing time set to ' + request.form['time']
    return render_template('coffee.html')
# @app.route('/newpage')
# def newpage():
    # return 'Second page if needed'

if __name__ == '__main__':
    state_machine_process = Thread(target = state_machine_handler)
    state_machine_process.start()
    app.run(use_reloader=False, debug = True, host = '0.0.0.0')
