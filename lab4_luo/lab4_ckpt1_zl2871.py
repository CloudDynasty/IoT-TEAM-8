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

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('room', '37288371')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.config('mac'))

do_connect()

response = urequests.get('https://restapi.amap.com/v3/ip?key=cd52b97d91ac9257b23862225c4db075')
parsed = response.json()
locstr = parsed["rectangle"]
print("locstr: " + locstr)
s1, s2 = locstr.split(';')
lon,lat = s1.split(',')

oled.fill(0)
oled.text(str("lon:" + lon), 0, 0)
oled.text(str("lat:" + lat), 0, 10)
oled.show()