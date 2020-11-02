import gc
import machine
import socket
import time
import network
import ssd1306
import urequests as requests
import json

# some global variables
page = 'home1' # home1, home2, display_time, set_time, set_alarm, display_weather, display_tweet, gesture_recognition, display_cmd
page_index = 0
week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
alarm_enable = 0
alarm_time = [0,1,0]
last_tweet = 'No tweet!'
last_cmd = 'No command!'
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)
buzzer = machine.Pin(15, machine.Pin.OUT)
oled_flag = True
### ----------------------------------- ###
# connect to Wi-Fi
'''
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('Jhone', 'libo2489')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())
'''
### ----------------------------------- ###
# set up server
'''
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('',80))
s.listen(5)
s.settimeout(0.1)
text = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
'''

### ----------------------------------- ###
# set up oled
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)



### ----------------------------------- ###
# set default time
'''
url = "https://worldtimeapi.org/api/ip"
res = requests.get(url).json()
time_now = res['datetime'].split('T')[1][0:8]
t = time_now.split(':')
day = res['datetime'].split('T')[0].split('-')
rtc = machine.RTC()
rtc.datetime((int(day[0]),int(day[1]),int(day[2]), 0, int(t[0]),int(t[1]),int(t[2]), 0))
'''
rtc = machine.RTC()
rtc.datetime((2020,1,1,0,0,0,40,0))
set_time = None





### ----------------------------------- ###
# button functions
# buttonA: select
def buttonAPressed(pin):
    value = pin.value()
    time.sleep_ms(50)
    if pin.value() != value:
        return
    global page
    global page_index
    if page == 'home1':
        page_index += 1
        if page_index >= 3:
            page = 'home2'
            page_index = 0
    elif page == 'home2':
        page_index += 1
        if page_index >= 3:
            page = 'home1'
            page_index = 0
    elif page == 'set_time':
        if page_index == 2:
            page_index = 4
        else:
            page_index = (page_index + 1) % 8
    elif page == "set_alarm":
        page_index = (page_index + 1) % 4

# buttonB: confirm
def buttonBPressed(pin):
    value = pin.value()
    time.sleep_ms(50)
    if pin.value() != value:
        return
    global page
    global page_index
    global set_time
    global alarm_time
    global alarm_enable
    if page == "home1":
        if page_index == 0:
            page = "display_time"
            page_index = 0
        elif page_index == 1:
            page = "set_time"
            page_index = 0
            set_time = list(rtc.datetime()[0:7])
        elif page_index == 2:
            page = "set_alarm"
            page_index = 0
    elif page == 'home2':
        if page_index == 0:
            page = "display_weather"
            page_index = 0
        elif page_index == 1:
            page = "display_tweet"
            page_index = 0
    elif page == 'set_time':
        if page_index == 7:
            rtc.datetime(tuple(set_time[0:7]+[0]))
            page = 'home1'
            page_index = 0
        else:
            set_time[page_index] += 1
    elif page == 'set_alarm':
        if page_index == 3:
            alarm_enable = 1 - alarm_enable
        else:
            alarm_time[page_index] += 1
        print(alarm_time, alarm_enable)

# buttonC: going back
def buttonCPressed(pin):
    value = pin.value()
    time.sleep_ms(50)
    if pin.value() != value:
        return
    global page
    global page_index
    page = 'home1'
    page_index = 0


### ----------------------------------- ###
# set button
buttonA = machine.Pin(13, machine.Pin.IN)
buttonB = machine.Pin(14, machine.Pin.IN)
buttonC = machine.Pin(12, machine.Pin.IN)
buttonA.irq(trigger=machine.Pin.IRQ_FALLING, handler=buttonAPressed)
buttonB.irq(trigger=machine.Pin.IRQ_FALLING, handler=buttonBPressed)
buttonC.irq(trigger=machine.Pin.IRQ_FALLING, handler=buttonCPressed)

# display contents
def display(contents, flag = oled_flag):
    # contents is array including 3 strings.
    # the length of each string is less than 16.
    # each string will be displayed in one line
    if flag:
        oled.fill(0)
        oled.text(contents[0], 0, 0)
        oled.text(contents[1], 0, 10)
        oled.text(contents[2], 0, 20)
        oled.show()
    else:
        oled.fill(0)
        oled.show()

# get weather
def get_weather():
    contents = ["This is a weather message","",""]
    '''
    post_data = json.dumps({})
    location_url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCtqxRLocPOWw63iDQEG4ogJ7BNWTJxi68'
    location_res = requests.post(location_url,data = post_data).json()
    lat = location_res['location']['lat']
    lng = location_res['location']['lng']
    weather_url = "http://api.openweathermap.org/data/2.5/weather?units=metric&lat="+ str(lat) + "&lon=" + str(lng) + "&appid=06ae078937fcc7026bf1944477ec40d5"
    weather_res = requests.get(weather_url).json()
    temp = weather_res['main']['temp']
    description = weather_res['weather'][0]['description']
    contents[0] = str(round(lat,2)) + ' , ' + str(round(lng,2))
    contents[1] = 'temp: ' + str(temp)
    contents[2] = description
    '''
    return contents

# display different contents according to different pages
def display_page(page):
    if page == 'home1':
        contents = ['1.Display Time', '2.Set Time', '3.Set Alarm']
        contents[page_index] = '> ' + contents[page_index]
        display(contents)
    elif page == 'home2':
        contents = ['4.Display Weather', '5.Display Tweet', '6.Gesture Recognition']
        contents[page_index] = '> ' + contents[page_index]
        display(contents)
    elif page == 'display_time':
        contents = ['','','']
        contents[0] = "date: " + str(rtc.datetime()[0]) + '-' + str(rtc.datetime()[1]) + '-' + str(rtc.datetime()[2])
        contents[1] = "time: " + str(rtc.datetime()[4]) + ':' + str(rtc.datetime()[5]) + ':' + str(rtc.datetime()[6])
        contents[2] = week[rtc.datetime()[3]]
        display(contents)
    elif page == 'set_time':
        contents = ['','','']
        tmp_time = list(set_time) + ['Confirm?']
        tmp_time[page_index] = '>' + str(tmp_time[page_index])
        contents[0] = "date: " + str(tmp_time[0]) + '-' + str(tmp_time[1]) + '-' + str(tmp_time[2])
        contents[1] = "time: " + str(tmp_time[4]) + ':' + str(tmp_time[5]) + ':' + str(tmp_time[6])
        contents[2] = tmp_time[7]
        display(contents)
    elif page == "set_alarm":
        contents = ['','','']
        alarm_text = 'Alarm: On' if alarm_enable else 'Alarm: Off'
        tmp_time = list(alarm_time) + [alarm_text]
        tmp_time[page_index] = '>' + str(tmp_time[page_index])
        contents[1] = tmp_time[3]
        contents[0] = "time: " + str(tmp_time[0]) + ':' + str(tmp_time[1]) + ':' + str(tmp_time[2])
        contents[2] = ""
        display(contents)
    elif page == "display_weather":
        contents = get_weather()
        display(contents)
    elif page == "display_tweet":
        contents = ['','','']
        contents[0] = last_tweet[0:16]
        if len(last_tweet) > 16:
            contents[1] = last_tweet[16:32]
        if len(last_tweet) > 32:
            contents[2] = last_tweet[32:48]
        display(contents)
    elif page == "gesture_recognition":
        pass
        ### Todo: gesture_recognition
        # use function 
    elif page == 'display_cmd':
        contents = ['','','']
        contents[0] = last_cmd[0:16]
        if len(last_cmd) > 16:
            contents[1] = last_cmd[16:32]
        if len(last_cmd) > 32:
            contents[2] = last_cmd[32:48]
        display(contents)

def alarm():
    for i in range(3):
        buzzer.value(1)
        led.value(0)
        time.sleep(0.5)
        display_page(page)
        buzzer.value(0)
        led.value(1)
        time.sleep(0.5)
        display_page(page)

def send_tweet(message):
    pass
    ### Todo: send tweet according to the message

def do_semthing(cmd):
    global oled_flag
    global page
    global last_tweet
    if page != 'home1' or page != 'home2':
        response = text + 'The system is busy, please try again later.'
        return response
    else:
        if cmd == '':
            response = text + 'No command found.'
            return response
        else:
            if 'TURN%20OFF' in cmd and 'DISPLAY' in cmd:
                oled_flag = False
                response = text + 'Do command successfully.'
            elif 'TURN%20ON' in cmd and 'DISPLAY' in cmd:
                oled_flag = True
                response = text + 'Show command successfully.'
            elif 'DISPLAY%20THE%20TIME' in cmd or 'DISPLAY%20TIME' in cmd:
                page = 'display_time'
                response = text + 'Display time successfully.'
            elif 'SEND%20TWEET' in cmd:
                ### Todo: send tweet
                # send_tweet(message)
                # last_tweet = message
                ###
                page = 'display_tweet'
                response = text + 'Send tweet successfully.'
            elif 'DISPLAY%20WEATHER' in cmd:
                page = 'display_weather'
                response = text + 'Display weather successfully.'
            else:
                page = 'display_cmd'
                response = text + 'Show command successfully.'
                return response

def main():
    while True:
        '''
        try:
            conn,addr=s.accept()
            request=conn.recv(1024)
            request=str(request)
            #cmd = request.split('/?cmd=')[1].split(' ')[0]
            #response=do_semthing(cmd)
            #conn.send(response)
            conn.close()
        except:
        '''
        display_page(page)
        if alarm_enable and (rtc.datetime()[4] == alarm_time[0] and rtc.datetime()[5] == alarm_time[1] and rtc.datetime()[6] == alarm_time[2]):
            alarm()
