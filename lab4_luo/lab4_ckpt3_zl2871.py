# This file is executed on every boot (including wake-boot from deepsleep)
# implement lab 3 code
import machine
import network
from machine import RTC, Pin, I2C, PWM, SPI
import urequests
import ujson
import time
import ssd1306

# setup the I2C communication with oled
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
# setup of pins corresponds to button on oled
pin0 = Pin(0, Pin.IN) # Button A

pressed = False
# Set alarm interrupt
def buttonPressed(p):
    global pressed
    time.sleep_ms(10)
    if p == 1:
        pressed = True
        print("pressed and checked!")


# setup the pins for button interrupt from oled board
pin0.irq(trigger=Pin.IRQ_RISING, handler=buttonPressed) # Button A
print("reached!")


while True:
    time.sleep_ms(10)
    if pressed:
        print("updated!")
        pressed = False
        myMes = 'Im doing lab4 demo!'
        response = urequests.get('https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=PNTXNFS5UPA5EHYG&status=' + myMes)
        time.sleep_ms(10)