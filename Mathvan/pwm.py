import RPi.GPIO as gpio
from datetime import datetime
from time import sleep, time



gpio.setmode(gpio.BCM)
gpio.setup(2, gpio.IN)
global risingCount
global pulseWidth
global timeStart
risingCount = 0
pulseWidth=0
timeStart=0

def edgeDetected(channel):

    global risingCount
    global pulseWidth
    global timeStart

    if gpio.input(2):
        #rising edge
        risingCount += 1
        timeStart = time()
    else:
        #falling edge
        if (risingCount != 0):
            timePassed = time() - timeStart
            #make pulseWidth an average
            pulseWidth = (((pulseWidth*(risingCount-1)) + timePassed)/risingCount)
            #print timePassed
gpio.add_event_detect(2, gpio.BOTH, callback=edgeDetected)

while True:
    sleep(1)
    pulseWidth =int(round(1000000*pulseWidth))

    print "PWM ={} ".format(pulseWidth)
    risingCount = 0
    pulseWidth = 0




