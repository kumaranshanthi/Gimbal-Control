import RPi.GPIO as gpio
import time, cv2, os
import os, time, math, glob, re
import pyexiv2, datetime, argparse
import fractions, dateutil.parser, shutil
import serial
import geotag_position

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

def frame_time(t):
    '''return a time string for a filename with 0.01 sec resolution'''
    # round to the nearest 100th of a second
    t += 0.005
    hundredths = int(t * 100.0) % 100
    return "%s%02uZ" % (time.strftime("%Y%m%d%H%M%S", time.gmtime(t)), hundredths)

 
def video_to_frames(video, path_output_dir):
	global ser
	global pulseWidth
	global risingCount

	camera = cv2.VideoCapture(video)

	#Set the camera resolution
	camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

	#grab an image just to activate the camera
	camera.grab()
	try:
		while True:
			PWM =int(round(1000000*pulseWidth))
			print ("PWM ={} ".format(PWM))
			risingCount = 0
			pulseWidth = 0
			if PWM > 1900 :	
				gps_data="$GPGGA,210230,3855.4487,N,09446.0071,W,1,07,1.1,370.5,M,-29.5,M,,*7A"
				ser.write(str.encode(gps_data))

				camera.grab()
				frametime = frame_time(time.time())

				return_value, image = camera.retrieve()

				filename=os.path.join(folder,frametime + '.jpg')
				cv2.imwrite(filename, image)
				lat,lon=geotag_position.parseGPS(ser)
				#print lat,lon           
				geotag_position.set_gps_location(filename, 12.888, 13.888, 100)   
				geotag_position.set_gps_location(filename, float(lat), float(lon), 100)         
				time.sleep(1)
			else:
				print("waiting for triger")
				time.sleep(1)
	except KeyboardInterrupt:
		pass

	#Finally, shutdown the camera
	print("Closing camera")
	del(camera)

gpio.setmode(gpio.BCM)
gpio.setup(2, gpio.IN)
global risingCount
global pulseWidth
global timeStart
global ser
risingCount = 0
pulseWidth=0
timeStart=0
port='/dev/ttyUSB0'
ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)
if __name__ == '__main__':
	#Open the default camera on the system
	#folder="/home/pi/Desktop/geotag/"
	folder="./geotag/"
	try:
		if not os.path.exists(folder):
			os.makedirs(folder)
	except OSError:
		print ('already created' +  folder)
	gpio.add_event_detect(2, gpio.BOTH, callback=edgeDetected)
	video_to_frames("/dev/video0", folder)
