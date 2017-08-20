
ID = '00:16:53:0C:CB:67'

# import the necessary packages
from shapedetector import ShapeDetector
import argparse
import imutils
import numpy as np
import cv2
import sys
import tty, termios
import tty

import nxt.locator
import thread
from nxt.motor import *
# This is all we need to import for the beep, but you'll need more for motors, sensors, etc.
from nxt.bluesock import BlueSock
from time import sleep
from nxt.sensor import *
import cv
import cv2.cv as cv
import time

KNOWN_WIDTH = {}

#KNOWN_DISTANCE = {}

focalLengths = {}

ROTATION = 90
PUISSANCE = 80
NBESSAIS = 6
DD = 360
MAXDISTANCEVIEW = 50
MINSHAPCONSIDIRE = 500
PRECISIONFORM = 0.015
DUREEATTENTECAM = 8
DV = 360

notrelacherpiece = True

IMAGE_PATHS = ["l80.png", "c80.png", "t80.png", "d80.png"]
d_shapes = ["pentagon","circle", "triangle",  "rectangle"]
d_colors = ["blue", "red", "green", "green"]

KNOWN_WIDTH["pentagon"] = 120
KNOWN_WIDTH["circle"] = 32
KNOWN_WIDTH["triangle"] = 48
KNOWN_WIDTH["rectangle"] = 110

d_cmpt = 0

def keeppiece(pick):
    while notrelacherpiece :
    	pick.turn(20, 50, False)

def runinstruction(pick):
    #keeppiece(pick)
    thread.start_new_thread(keeppiece,(pick,))

def play(brick):
    brick.play_tone_and_wait(440, 1000)

def getch() :
	print "Quelle action voulez vous faire?"
	print "1 : Aller l'ile cerculaire rouge"
	print "2 : Aller l'ile triangulaire rouge"
	print "3 : Aller l'ile cerculaire jaune"
	print "4 : Aller l'ile caree jaune"
	print "5 : Aller l'ile polygone verte"
	print "6 : Aller l'ile triangulaire verte"
	print "7 : Aller l'ile carree verte"
	print "8 : Aller s'approvisionner a l'ile polygone bleu"
	print "9 : Lancer le calibrage"
	print "e : Marcher Avant"
	print "d : Reculer"
	print "f : Tourner a droite"
	print "s : Tourner a gauche"
	print "q : Quitter"
	print "c : Pour capturer la piece metalique"
	print "r : Pour relacher la piece metalique"

	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
	 tty.setraw(fd)
	 ch = sys.stdin.read(1)
	finally:
	 termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch


ch = ' '
print "Ready"

#fin all the 'yellow shapes in the image'
lowerRed2 = np.array([160, 100, 100],np.uint8)
upperRed2 = np.array([179, 255, 255],np.uint8)
lowerRed1 = np.array([0, 100, 100],np.uint8)
upperRed1 = np.array([10, 255, 255],np.uint8)

#fin all the 'blue shapes in the image'
lowerBlue1 = np.array([110,150,150],np.uint8)
upperBlue1 = np.array([130,255,255],np.uint8)
lowerBlue2 = np.array([100,150,0],np.uint8)
upperBlue2 = np.array([140,255,255],np.uint8)

#fin all the 'yellow shapes in the image'
lowerYellow1 = np.array([20, 100, 100],np.uint8)
upperYellow1 = np.array([32, 255, 255],np.uint8)
lowerYellow2 = np.array([15, 100, 100],np.uint8)
upperYellow2 = np.array([20, 255, 255],np.uint8)

#fin all the 'yellow shapes in the image'
lowerGreen1 = np.array([40, 100, 50],np.uint8)
upperGreen1 = np.array([80, 255, 255],np.uint8)
lowerGreen2 = np.array([45,100,100],np.uint8)
upperGreen2 = np.array([75,255,255],np.uint8)

def getShapeColorFromImage(image, form, color) :
	#appliquer filtre pour enlever les parasites de l image
	median = cv2.medianBlur(image,9)
	hsv_img = cv2.cvtColor(median,cv2.COLOR_BGR2HSV)

	shapeMask1 = cv2.inRange(hsv_img, lowerBlue1, upperBlue1)
	shapeMask2 = cv2.inRange(hsv_img, lowerBlue2, upperBlue2)
	if color == "red":
		shapeMask1 = cv2.inRange(hsv_img, lowerRed1, upperRed1)
		shapeMask2 = cv2.inRange(hsv_img, lowerRed2, upperRed2)          
	elif color == "yellow":
		shapeMask1 = cv2.inRange(hsv_img, lowerYellow1, upperYellow1)
		shapeMask2 = cv2.inRange(hsv_img, lowerYellow2, upperYellow2)     
	elif color == "green":
		shapeMask1 = cv2.inRange(hsv_img, lowerGreen1, upperGreen1)
		shapeMask2 = cv2.inRange(hsv_img, lowerGreen2, upperGreen2)
	else:
		shapeMask1 = cv2.inRange(hsv_img, lowerBlue1, upperBlue1)
		shapeMask2 = cv2.inRange(hsv_img, lowerBlue2, upperBlue2)

	shapeMask = cv2.addWeighted(shapeMask1, 1.0, shapeMask2, 1.0, 0.0)

	# find contours in the thresholded image and initialize the
	# shape detector
	cnts,hierarchy = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_TC89_KCOS)

	print "I found %d  shapes" % (len(cnts))

	#cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	sd = ShapeDetector()
	# loop over the contours
	for c in cnts:
		ca = cv2.contourArea(c)
		if ca > MINSHAPCONSIDIRE:
			print "ca =  %d " % (ca)
			
			shape = sd.detect(c)
			print shape
			if form == shape :
				peri = cv2.arcLength(c, True)
				approx = cv2.approxPolyDP(c, PRECISIONFORM * peri, True)
				return approx
	return None

for shape in d_shapes :
	image = cv2.imread(IMAGE_PATHS[d_cmpt])
	val = getShapeColorFromImage(image, shape, d_colors[d_cmpt])
	if val is not None:
		focalLengths[shape] = (cv2.contourArea(val) * 60) / KNOWN_WIDTH[shape]
		print 'Le focus de la form  %s = %d' % (shape, focalLengths[shape]) 
	d_cmpt = d_cmpt + 1			 
def getDistanceFromCam(frame, shape) :
	distance = focalLengths[shape] * KNOWN_WIDTH[shape] / cv2.contourArea(frame)
	return distance


def getImageFromCam() :
	cap=cv2.VideoCapture(-1)
	#cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, int(352))
	#cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, int(288))
	#cap.set(cv2.cv.CV_CAP_PROP_FPS,5)
	ret, frame = cap.read()
	del(cap)
	return frame

def calibreCamera() :
	frame = getImageFromCam()
	shapes = ["circle", "pentagon", "rectangle", "triangle"]
	colors = [ "green", "yellow"]
	for color in colors :
		tmp = 0
		for shape in shapes :
			if tmp > 0 : 
				break
			val = getShapeColorFromImage(frame, shape, color)
			if val is not None:
				tmp = 1
				print 'quel est la distance du %s %s' % (shape, color)
				data = input("Entrer un numero: ") 
				#KNOWN_DISTANCE[shape] = data
				width = input("Quelle est la superficie de la forme: ")
				KNOWN_WIDTH[shape] = width
				focalLengths[shape] = (cv2.contourArea(val) * data) / KNOWN_WIDTH[shape]
	print "Calibrage terminer"




	
sock =  BlueSock(ID)
if sock :
	brick = sock.connect()
	left = nxt.Motor(brick, PORT_A)
	right = nxt.Motor(brick, PORT_B)
	pick = nxt.Motor(brick, PORT_C)
	both = nxt.SynchronizedMotors(left, right, 0)
	leftboth = nxt.SynchronizedMotors(left, right, 100)
	rightboth = nxt.SynchronizedMotors(right, left, 100)


	while ch != 'q':
		compteur = 0
		ch = getch()
		print "Execution de la tache demander"
		if ch == 'e':
		    both.turn(PUISSANCE, DD, False)
		elif ch == 'd':
		    both.turn(-1*PUISSANCE, DD, False)
		elif ch == 's':
		    leftboth.turn(PUISSANCE, ROTATION, False)
		elif ch == 'f':
		    rightboth.turn(PUISSANCE, ROTATION, False)
		elif ch == 'c':
		    notrelacherpiece = True
		    runinstruction(pick)
		elif ch == 'r':
		    notrelacherpiece = False
		elif ch == '9':
			frame = getImageFromCam()
			shapes = ["circle", "pentagon", "rectangle", "triangle"]
			colors = [ "green", "yellow"]
			for color in colors :
				tmp = 0
				for shape in shapes :
					if tmp > 0 : 
						break
					val = getShapeColorFromImage(frame, shape, color)
					if val is not None:
						tmp = 1
						print 'quel est la distance du %s %s' % (shape, color)
						data = input("Entrer un numero: ") 
						#KNOWN_DISTANCE[shape] = data
						width = input("Quelle est la superficie de la forme: ")
						KNOWN_WIDTH[shape] = width
						focalLengths[shape] = (cv2.contourArea(val) * data) / KNOWN_WIDTH[shape]
			print "Calibrage terminer"
		else :
			shape = "pentagon"
			color = "blue"
			while compteur < NBESSAIS :
				if ch == '1' :
					#shape = "circle"
					shape = "pentagon"
					color = "red"
				elif ch == '2':
					shape = "triangle"
					color = "red"
				elif ch == '3':
					shape = "circle"
					color = "yellow"
				elif ch == '4':
					shape = "rectangle"
					color = "yellow"
				elif ch == '5' :
					shape = "pentagon" 
					color = "green"
				elif ch == '6' :
					shape = "triangle"
					color = "green"
				elif ch == '7':
					shape = "rectangle" 
					color = "green"
				elif ch == '8' and shape == "pentagon":
					shape == "pentagon"
					color = "blue"
				# Capture frame-by-frame
				frame = getImageFromCam()
				val = getShapeColorFromImage(frame, shape, color)
				if val is not None:
					play(brick)
					distance = getDistanceFromCam(val, shape)
					print "distance = %d" % (distance)
					if distance > MAXDISTANCEVIEW :
						allera = distance - (MAXDISTANCEVIEW - 1)
						both.turn(PUISSANCE, 20*distance, False) 
						break #compteur = 0
					else :
						both.turn(PUISSANCE, 20*distance , False)
						break
				else :
					compteur = compteur + 1
					leftboth.turn(PUISSANCE, ROTATION, False)
				time.sleep(DUREEATTENTECAM)
	sock.close() 



	
		    
		 
			
        



