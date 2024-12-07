#include "mbed.h"
#include <cstdint>
#include "uLCD.hpp"

// states: {0: idle (not brewing, clean), 1: brewing, 2: finished (not brewing, dirty)}

#define PIN_STATE_LSB p26
#define PIN_STATE_MSB p25

#define ONE_SECOND 25000000
#define COFFEE_STATE (coffee_state_msb.read() << 1) | coffee_state_lsb.read()

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);

// State signals from RPI
DigitalIn   coffee_state_lsb(PIN_STATE_LSB);
DigitalIn   coffee_state_msb(PIN_STATE_MSB);

int main() {

    uint8_t state = (coffee_state_msb.read() << 1) | coffee_state_lsb.read();

    // initialize lcd
    uLCD LCD(p28, p27, p30, uLCD::BAUD_1500000);
    printf("instantiated LCD\n");

    // check state and print message on lcd
    while (true) {
        state = (coffee_state_msb.read() << 1) | coffee_state_lsb.read();
        printf("state : %d", state);
        LCD.cls();

        switch(state) {
            case 0x0 :
                LCD.printf("\nReady to brew !!!\n");
                led1.write(0);
                led2.write(0);
            break;
            case 0x2 :
                LCD.printf("\nBrewing...\n");
                led1.write(1);
                led2.write(0);
            break;
            case 0x1 :
                LCD.printf("Pls clean me :)\n");
                led1.write(0);
                led2.write(1);
            break;

            // this state should never occur
            case 0x3 :
                LCD.printf("\nhow did you get here ?\n");
                led1.write(1);
                led2.write(1);
            break;
        }
        wait_us(1500000);
    }
    // uLCD_4DGL uLCD(p27,p28,p30); // serial tx, serial rx, reset pin;

    return 0;
}