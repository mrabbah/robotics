
ID = '00:16:53:0C:CB:67'

import nxt.locator
import thread
from nxt.motor import *
# This is all we need to import for the beep, but you'll need more for motors, sensors, etc.
from nxt.bluesock import BlueSock
from time import sleep
from nxt.sensor import *
import numpy as np
import cv2,cv
import cv2.cv as cv
import time
import numpy as np
import cv2


def find_marker(image):
	# convert the image to grayscale, blur it, and detect edges
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 35, 125)

	# find the contours in the edged image and keep the largest one;
	# we'll assume that this is our piece of paper in the image
	(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	c = max(cnts, key = cv2.contourArea)

	# compute the bounding box of the of the paper region and return it
	return cv2.minAreaRect(c)

def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the maker to the camera
	return (knownWidth * focalLength) / perWidth

# initialize the known distance from the camera to the object, which
# in this case is 24 inches
KNOWN_DISTANCE = 60

# initialize the known object width, which in this case, the piece of
# paper is 12 inches wide
KNOWN_WIDTH = 7.6

# initialize the list of images that we'll be using
IMAGE_PATHS = ["images/60.jpg", "images/50.jpg", "images/40.jpg", "images/70.jpg", "images/100.jpg"]

# load the furst image that contains an object that is KNOWN TO BE 2 feet
# from our camera, then find the paper marker in the image, and initialize
# the focal length
image = cv2.imread(IMAGE_PATHS[0])
marker = find_marker(image)
focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH

cap=cv2.VideoCapture(-1)
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, int(320))
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, int(240))
cap.set(cv2.cv.CV_CAP_PROP_FPS,5)


while(True):
		# Capture frame-by-frame
		ret, frame = cap.read()
		marker = find_marker(frame)
		cm =  distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
		# draw a bounding box around the image and display it
		box = np.int0(cv2.cv.BoxPoints(marker))
		#cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),1)
		#cv2.drawContours(marker, [box], -1, (0, 255, 0), 2)
		#cv2.putText(marker, "%.2fcm" % (cm), (marker.shape[1] - 200, marker.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 3)
		print(("distance en cm = %d" % cm))
		# Display the resulting frame
		cv2.imshow('img',frame)
		sock = 	BlueSock(ID)
		if sock:
				brick = sock.connect()
				mx = Motor(brick, nxt.PORT_A)
				my = Motor(brick, nxt.PORT_B)
				left = nxt.Motor(brick, PORT_A)
				right = nxt.Motor(brick, PORT_B)
				both = nxt.SynchronizedMotors(left, right, 0)
				leftboth = nxt.SynchronizedMotors(left, right, 100)
				rightboth = nxt.SynchronizedMotors(right, left, 100)
				motors = [mx, my]
				
				if cm:
					
					brick.play_tone_and_wait(440, 100)
					both.turn(100, 20*cm, False)
					 
					mx.turn(10, 10)
					my.turn(10, 10)
		else:
				print 'No NXT bricks found'	
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	
# When everything done, release the capture
time.sleep(0)
cap.release()
cv2.destroyAllWindows()
sock.close()	
