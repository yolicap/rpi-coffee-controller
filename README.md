# Raspberry Pi Smart Coffee ☕️

Explenation blah blah blah

## State Machine

<add more details???>

States:
- 0 : Ready
- 1 : Brewing
- 2 : Finished/Dirt

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

kathie write stuff here
<picture of UI>

## Dependencies
- [pigpio](https://abyz.me.uk/rpi/pigpio/index.html) - raspberry pi gpio deamon plus python pigpio library
- [Flask](https://flask.palletsprojects.com/en/stable/) - python web app framework
- [pyserial](https://pyserial.readthedocs.io/en/latest/) - python serial library used to communicate with LCD
