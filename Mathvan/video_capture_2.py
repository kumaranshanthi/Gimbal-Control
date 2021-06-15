
import time, cv2, os
import os, time, math, glob, re
import pyexiv2, datetime, argparse
import fractions, dateutil.parser, shutil
import serial
import geotag_position


def frame_time(t):
    '''return a time string for a filename with 0.01 sec resolution'''
    # round to the nearest 100th of a second
    t += 0.005
    hundredths = int(t * 100.0) % 100
    return "%s%02uZ" % (time.strftime("%Y%m%d%H%M%S", time.gmtime(t)), hundredths)

 
def video_to_frames(video, path_output_dir):
	global ser
	

	camera = cv2.VideoCapture(video)

	#Set the camera resolution
	camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

	#grab an image just to activate the camera
	camera.grab()
	try:
		while True:
		
			gps_data="$GPGGA,210230,3855.4487,N,09446.0071,W,1,07,1.1,370.5,M,-29.5,M,,*7A"
			ser.write(str.encode(gps_data))

			camera.grab()
			frametime = frame_time(time.time())
			return_value, image = camera.retrieve()
			#print frametime

			filename=os.path.join(folder,frametime + '.jpg')
			print filename
			cv2.imwrite(filename, image)
			lat,lon=geotag_position.parseGPS(ser)
			#print lat,lon           
			geotag_position.set_gps_location(filename, float(lat), float(lon), 100)         
			time.sleep(1)
			
	except KeyboardInterrupt:
		pass

	#Finally, shutdown the camera
	print("Closing camera")
	del(camera)


port='/dev/ttyUSB0'
ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)
if __name__ == '__main__':
	#Open the default camera on the system

	folder="./geotag/"
	try:
		if not os.path.exists(folder):
			os.makedirs(folder)
	except OSError:
		print ('already created' +  folder)
	video_to_frames("/dev/video0", folder)
