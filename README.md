# Raspberry Pi Smart Coffee ☕️

## State Machine

statemachine.py is a Moore state machine that controls the state of our system.

Outputs:
- LEDs: green: Ready; blue: Brewing; red: Finished/Dirty
- uLCD: displays the current state
- signals to the peripheral board, implemented by other controllers

Inputs:
- brew button
- clean button
- HTTP requests to our web server
- Timer

States:
- 0 : Ready
- 1 : Brewing
- 2 : Finished/Dirty

When in state 0: set the LED to green and display "ready to brew" on LCD. If the brew button is pressed, there is a request to brew from the web server, or if the timer for preset brewing* has completed, move to state 1.
When in state 1: set the LED to blue and display "brewing" on LCD. If a cancel request from the web server is received or if the brewing timer (set in BrewerController), move to state 2.
When in state 2: set LED to red and display "need cleaning" on LCD. If the clean button is pressed, move to state 0.

* A timer for preset brewing is set when the user chooses a time on the web application. app.py sets the time in statemachine.py and starts a timer.

## Peripheral Controllers
For each major component there is a controller class that objectifies peripherals connected to the raspberry pi. An instance of a `pigpio` connection is passed when initating each controller. Controller objects are initiated in the application.

### LCDController

The `LCDController` creates a serial connection with the LCD [(uLCD-144-G2)](https://www.mouser.com/datasheet/2/451/uLCD_144_G2_Datasheet_R_1_6-1627133.pdf) when `init()` is called. This is primarly used to write text messages on the LCD in order to tell the user the current state of the coffee machine. Commands [Serial Command Reference Manual](https://cdn.sparkfun.com/assets/a/b/1/7/a/goldelox_serialcmdmanual.pdf) from the are transmitted using `pyserial` library.

### BrewerController

The `BrewerController` controls different components in the original PCB that came with the coffee machine including the heater that brews the coffee. The PCB has 4 connections excluding power and ground. One of these connections is for a buzzer, another is for the heater, and the two other ones are not exactly known. It's possible that one of them could be data from the thermostat that measures temperature from the heating pad. `brew()` sets a timer for `s` seconds. When the timer is finished, an interrupt calls `stop_brew()`. Ideally, it would be good to use data from the thermostat but this feature is skipped due to time constraint.

<picutre of brewer pcb>

### MiscController

`MiscController` is responsible for controlling miscellanious peripherals that are not complicated enough to have their own controller like LEDs, buttons, etc.

## Web App
Our system is ran starting from app.py. It creates an instance of the state machine and starts it. On the web page, the user can press a button to start brewing, to cancel brewing, set a time to brew at every day automcatically, and remove the automatic brewing.
<picture of UI>

## Dependencies
- [pigpio](https://abyz.me.uk/rpi/pigpio/index.html) - raspberry pi gpio deamon plus python pigpio library
- [Flask](https://flask.palletsprojects.com/en/stable/) - python web app framework
- [pyserial](https://pyserial.readthedocs.io/en/latest/) - python serial library used to communicate with LCD
