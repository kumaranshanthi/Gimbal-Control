import cv2
import os
from datetime import datetime

import time
import os



def video_to_frames(video, path_output_dir):
    # extract frames from a video and save to directory as 'x.png' where 
    # x is the frame index
    vidcap = cv2.VideoCapture(video)
    count = 0
    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            cv2.imwrite(os.path.join(path_output_dir, '%d.jpg') % count, image)
            count += 1
	    time.sleep(0.5)
	    if cv2.waitKey(1) & 0xFF == ord('q'):
            	break
	else:
		break

        
    vidcap.release()
    cv2.destroyAllWindows()



today = datetime.now()

folder="./" + today.strftime('%Y%m%d_%H%M%S')
try:
	if not os.path.exists(folder):
		os.makedirs(folder)
except OSError:
	print ('already created' +  folder)


video_to_frames("/dev/video0", folder)

