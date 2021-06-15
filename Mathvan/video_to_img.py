import RPi.GPIO as gpio
from datetime import datetime
from time import sleep, time
import cv2
import os

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

def video_to_frames(video, path_output_dir):
	global pulseWidth
	global risingCount
	# extract frames from a video and save to directory as 'x.png' where 
	# x is the frame index
	vidcap = cv2.VideoCapture(video)
	count = 0
	while vidcap.isOpened():
		PWM =int(round(1000000*pulseWidth))
		print ("PWM ={} ".format(PWM))
		risingCount = 0
		pulseWidth = 0
		if PWM > 1900 :		
			success, image = vidcap.read()
			if success:
				cv2.imwrite(os.path.join(path_output_dir, '%d.png') % count, image)
				count += 1
				sleep(0.5)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
			else:
				break

		else:
			print("waiting for triger")
			sleep(1)
	vidcap.release()
	cv2.destroyAllWindows()



today = datetime.now()

folder="/home/pi/Desktop/image/" + today.strftime('%Y%m%d_%H%M%S')
try:
	if not os.path.exists(folder):
		os.makedirs(folder)
except OSError:
	print ('already created' +  folder)



gpio.add_event_detect(2, gpio.BOTH, callback=edgeDetected)



video_to_frames("/dev/video0", folder)



