# This file is executed on every boot (including wake-boot from deepsleep)
# implement lab 3 code
import machine
import network
from machine import RTC, Pin, I2C, PWM, SPI
import urequests
import ujson
import time
import ssd1306

# Connect with WiFi
# TODO: change the WiFi ID and password to those of your own
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('room', '37288371')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())
# Configure socket for data transmission
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('',80))
s.listen(5)
s.settimeout(1)

text = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'

# setup the I2C communication with oled
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
# setup of pins corresponds to button on oled
pin0 = Pin(0, Pin.IN) # Button A

pressed = False
# Set alarm interrupt
def buttonPressed(p):
    global pressed
    irq_state = machine.disable_irq()
    time.sleep_ms(10)
    if p == 1:
        pressed = True
        print("pressed and checked!")
    machine.enable_irq(irq_state)


# setup the pins for button interrupt from oled board
pin0.irq(trigger=Pin.IRQ_RISING, handler=buttonPressed) # Button A
print("reached!")

# Custom function for displaying message on oled
def display_cmd(cmd):
    oled.fill(0)
    oled.text(cmd[:16],0,0)
    if len(cmd) >= 16:
        oled.text(cmd[16:],0,10)
    if len(cmd) >= 32:
        oled.text(cmd[32:],0,20)
    if len(cmd) >= 48:
        oled.text('...',0,25)
    oled.show()

while True:
    if pressed:
        pressed = False # toggle the flag
        # get request and cmd
        conn, addr = s.accept()
        request=conn.recv(1024)
        request=str(request)
        cmd = request.split('/?cmd=')[1].split(' ')[0]
        # clear the %20 in cmd
        cleared = []
        i = 0
        while i < len(cmd):
            if cmd[i:i + 3] == '%20':
                cleared.append(' ')
                i = i + 3
            else:
                cleared.append(cmd[i])
                i = i + 1
        cleared = ''.join(cleared)
        # send request to thingspeak
        # TODO: modify to your own api key
        response = urequests.get('https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=PNTXNFS5UPA5EHYG&status=' + cleared)
        display_cmd(cleared)
        print(cleared)
        # compose and send android response
        response_Android = text + cleared
        conn.send(response)
        conn.close()
        time.sleep_ms(10)