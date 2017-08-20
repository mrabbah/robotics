
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
import requests
import json
import math

headers = {'content-type': 'application/json'}
base_url = 'http://192.168.0.104:8080/ObstacleAvoidance/ws/'
url_getTrajet = base_url + 'getTrajet'
url_getMap = base_url + 'getMap'
url_getOptimizedMap = base_url + 'getOptimizedMap'
url_getOptimizedTrajet = base_url + 'getOptimizedTrajet'
url_saveMap = base_url + 'saveMap'
url_saveTrajet = base_url + 'saveTrajet'

left = None
right = None
both = None
leftboth = None
rightboth = None
ultrasonic = None

ROTATION_GAUCHE = 110
ROTATION_DROITE = 130
PUISSANCE = 80
DD = 400
mymap = []
trajet = []
depart = [0, 0]
arrive = [0, 0]
position = [0, 0, 0]
runrobot = False
DUREESLEEP = 1 #une seconde
lignes = 1
colonnes = 1
DIRECTION = 0 #0 tout droit 1 a droite
DISTANCEOBSTACLE = 40 #40 cm

def reinisialiserMap():
	#mymap = []
	for y in range(0, lignes):
		vecteur = []
		for x in range(0, colonnes):
			vecteur.append(1)
		mymap.append(vecteur)
		print mymap

def afficherMap() :
	y = len(mymap)
	while(y > 0) :
		print mymap[y - 1]
		y = y -1
	

def callserver(url, params):
	r = requests.post(url, params=params, headers=headers)
	response =  r.json()
	return response

def play(brick):
    brick.play_tone_and_wait(440, 1000)

def verifierObstacle() :
	distance = ultrasonic.get_sample()
	if distance < DISTANCEOBSTACLE:
		return True
	else:
		return False

def getDistanceFromObstacle() :
	print 'La distance est'
	distance = ultrasonic.get_sample()
	print distance

def tournerDroite() :
	rightboth.turn(PUISSANCE, ROTATION_DROITE, False)
	time.sleep(DUREESLEEP)

def tournerGauche() :
	leftboth.turn(PUISSANCE, ROTATION_GAUCHE, False)
	time.sleep(DUREESLEEP)

def avancer() :
	both.turn(PUISSANCE, DD, False)
	time.sleep(DUREESLEEP)

def reculer() :
	both.turn(-1*PUISSANCE, DD, False)
	time.sleep(DUREESLEEP)

def getDistance(p1, p2):
	#print 'calcul distance entre '
	#print p1
	#print p2
	return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2)) 

def runrobot():
	print "Thread lance"
	global DIRECTION
	global trajet
	global mymap
	global position
	global runrobot

	runrobot = False
	while True :
		if(runrobot):
			current_d = getDistance(arrive, position)
			if(current_d == 0):
				print '+++++++++++++++++++++ Arrive +++++++++++++++++++++++++++'
				runrobot = False
				continue
			else :
				existeObstacle = verifierObstacle()
				#print existeObstacle
				
				lastelemntindex = len(trajet) - 1
				if(existeObstacle):
					tournerDroite()
					if(DIRECTION == 0):
						mymap[position[1] + 1][position[0]] = 0
					elif(DIRECTION == 1):
						mymap[position[1]][position[0] + 1] = 0
					elif(DIRECTION == 3):
						mymap[position[1]][position[0] - 1] = 0
					elif(DIRECTION == 2):
						mymap[position[1] - 1][position[0]] = 0
					DIRECTION = (DIRECTION + 1) % 4										
				else :
					p1 = [position[0], position[1] + 1]
					p2 = [position[0] + 1, position[1]]
					p3 = [position[0] - 1, position[1]]
					p4 = [position[0], position[1] - 1]
					d1 = getDistance(arrive, p1)
					d2 = getDistance(arrive, p2)
					d3 = getDistance(arrive, p3)
					d4 = getDistance(arrive, p4)
					if(position[1] + 1 >= lignes or mymap[position[1] + 1][position[0]] == 0):
						d1 = 9999999 #Valeur infini
					#print 'd1 = %f' % d1					
					if(position[0] + 1 >= colonnes or mymap[position[1]][position[0] + 1] == 0):
						d2 = 9999999 #Valeur infini
					#print 'd2 = %f' % d2
					if(position[0] - 1 < 0 or mymap[position[1]][position[0] - 1] == 0):
						d3 = 9999999 #Valeur infini
					#print 'd3 = %f' % d3
					if(position[1] - 1 < 0 or mymap[position[1] - 1][position[0]] == 0):
						d4 = 9999999 #Valeur infini
					#print 'd4 = %f' % d4

					if(len(trajet) >= 2) : #on veut eliminer le retour a etape moins un
						point_X_Y_MOINS_2 = trajet[lastelemntindex - 1]
						if(p1[0] == point_X_Y_MOINS_2[0] and p1[1] == point_X_Y_MOINS_2[1]):
							d1 = 9999999
						elif(p2[0] == point_X_Y_MOINS_2[0] and p2[1] == point_X_Y_MOINS_2[1]):
							d2 = 9999999
						elif(p3[0] == point_X_Y_MOINS_2[0] and p3[1] == point_X_Y_MOINS_2[1]):
							d3 = 9999999
						elif(p4[0] == point_X_Y_MOINS_2[0] and p4[1] == point_X_Y_MOINS_2[1]):
							d4 = 9999999

					if(d1 == 9999999 and d2 == 9999999 and d3 == 9999999 and d4 == 9999999): #cas ou le robot est coince
						print '+++++++++++++++++++++ Robot coince +++++++++++++++++++++++++++'
						runrobot = False
						continue
					action = 0 # 0 haut 1 a droite 2 a bas 3 gauche
					nxt_point = p1
					d = d1
					if(d2 < d):
						d = d2
						action = 1
						nxt_point = p2
					if(d3 < d):
						d = d3
						action = 3
						nxt_point = p3
					if(d4 < d):
						d = d4
						action = 2
						nxt_point = p4
					print 'action = %d' % action
					while (DIRECTION != action):
						if(action - DIRECTION >= 0):
							DIRECTION = (DIRECTION + 1) % 4
							tournerDroite()
						else:
							DIRECTION = (DIRECTION - 1) % 4
							tournerGauche()
						
					#trajet[lastelemntindex][2] = DIRECTION
					avancer()
					position = [nxt_point[0], nxt_point[1], DIRECTION]
					newpos = position[:]
					trajet.append(newpos)
		else:
			time.sleep(DUREESLEEP)


def runinstruction():
    thread.start_new_thread(runrobot,())

def getch() :
	print "Quelle action voulez vous faire?"
	print "1 : Entrer les coordonnees de depart"
	print "2 : Entrer les coordonnees d arrive"
	print "3 : Entrer la dimension de la carte"
	print "4 : Lancer le robot"
	print "5 : Arreter le robot"
	print "6 : Afficher Map"
	print "7 : afficher Trajet"
	print "9 : Envoyer donner au serveur"
	print "8 : Distance de obstacle"
	print "e : Marcher Avant"
	print "d : Reculer"
	print "f : Tourner a droite"
	print "s : Tourner a gauche"
	print "q : Quitter"

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


	
sock =  BlueSock(ID)
if sock :
	global DIRECTION
	global trajet
	global mymap
	global position
	global runrobot
	global both
	global leftboth
	global rightboth
	global ultrasonic
	brick = sock.connect()
	left = nxt.Motor(brick, PORT_A)
	right = nxt.Motor(brick, PORT_B)
	ultrasonic = Ultrasonic(brick, PORT_4)

	both = nxt.SynchronizedMotors(left, right, 0)
	leftboth = nxt.SynchronizedMotors(left, right, 100)
	rightboth = nxt.SynchronizedMotors(right, left, 100)

	runinstruction()

	while ch != 'q':
		ch = getch()
		print "Execution de la tache demander"
		if ch == 'e':
		    both.turn(PUISSANCE, DD, False)
		elif ch == 'd':
		    reculer()
		elif ch == 's':
		    tournerGauche()
		elif ch == 'f':
		    tournerDroite()
		elif ch == '1':
			line = sys.stdin.readline()
			chars = line.split(',')
			depart[0] = int(chars[0])
			depart[1] = int(chars[1])
			position[0] = depart[0]
			position[1] = depart[1]
			position[2] = 0
			#trajet = []
			newpos = position[:]
			trajet.append(newpos)
		elif ch == '2':
			line = sys.stdin.readline()
			chars = line.split(',')
			arrive[0] = int(chars[0])
			arrive[1] = int(chars[1])
		elif ch == '3':
			line = sys.stdin.readline()
			chars = line.split(',')
			lignes = int(chars[1])
			colonnes = int(chars[0])
			reinisialiserMap()
			print 'La nouvelle map :'
			afficherMap()
		elif ch == '4':
			runrobot = True
		elif ch == '5':
			runrobot = False
		elif ch == '6':
			afficherMap()
		elif ch == '7':
			print trajet
		elif ch == '8':
			getDistanceFromObstacle()
		elif ch == '9':
			callserver(url_saveTrajet, {'trajet': json.dumps(trajet)})
			callserver(url_saveMap, {'map': json.dumps(mymap)})
			
			
		
		    
		
#				time.sleep(DUREEATTENTECAM)
	sock.close() 
