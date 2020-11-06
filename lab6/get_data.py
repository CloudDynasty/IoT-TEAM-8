import machine
import ssd1306
import network, time
import socket
import urequests as requests

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('94CN6', 'WC210460')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('',80))
s.listen(5)
s.settimeout(1)
text = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
spi = machine.SPI(-1, baudrate=100000, polarity=1, phase=1, sck=machine.Pin(14), mosi=machine.Pin(13), miso=machine.Pin(12), bits=8)
cs = machine.Pin(3, machine.Pin.OUT, value=1)

btnA = False
btnB = False
btnC = False
# button functions
def buttonAPressed(pin):
    global btnA
    value = pin.value()
    time.sleep_ms(20)
    if pin.value() != value:
        return
    btnA = True

def buttonBPressed(pin):
    global btnB
    value = pin.value()
    time.sleep_ms(20)
    if pin.value() != value:
        return
    btnB = True


### ----------------------------------- ###
# set button
buttonA = machine.Pin(2, machine.Pin.IN)
buttonB = machine.Pin(0, machine.Pin.IN)

buttonA.irq(trigger=machine.Pin.IRQ_FALLING, handler=buttonAPressed)
buttonB.irq(trigger=machine.Pin.IRQ_FALLING, handler=buttonBPressed)


url = "http://3.19.229.147:8080/"
x0 = 0
y0 = 0
z0 = 0

while True:
    if btnA:  # buttonA is pressed, start recording
        print("start")
        record_data = []
        for i in range(15):
            cs.value(0)
            spi.write(b'\xF2')  # address=0x32  address + 0xC0 to set first two bits '11'
            x1, x2, y1, y2, z1, z2 = spi.read(6)
            cs.value(1)
            x0 += (x2 - x1)
            y0 += (y2 - y1)
            z0 += (z2 - z1)
            record_data.append((x0,y0,z0))
            time.sleep_ms(200)
        for j in range(15):
            body = {"x":record_data[j][0], "y":record_data[j][1], "z":record_data[j][2]}
            sendDataToServer = requests.post(url + "post", json=body)
            status = sendDataToServer.text
        print("posted a set of 15 values")

    if btnB:  # buttonB is pressed, stop and upload recording
        x0 = 0
        y0 = 0
        z0 = 0
        body = {"x": x0, "y": y0, "z": z0} # use x=0,y=0,z=0 to separate data
        sendDataToServer = requests.post(url + "post", json=body)
        status = sendDataToServer.text
        time.sleep_ms(10)
        print("end")
        downloadCSV = requests.get(url + "download")
        status = downloadCSV.text
        btnA = False
        btnB = False

