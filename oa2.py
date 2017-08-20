
# import the necessary packages
import sys
import tty, termios
import tty

import thread
from time import sleep
import time
import requests
import json
import math
import RPi.GPIO as gpio

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

ROTATION = 80
PUISSANCE = 80
DD = 340
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
tf = 0.25
tf_gauche = 0.6
tf_droite = 0.4
TRIG = 12
ECHO = 16

def init() :
	gpio.setmode(gpio.BOARD)
	gpio.setup(7, gpio.OUT)
	gpio.setup(11, gpio.OUT)
	gpio.setup(13, gpio.OUT)
	gpio.setup(15, gpio.OUT)
	gpio.setup(TRIG,gpio.OUT)
	gpio.output(TRIG,0)
	gpio.setup(ECHO,gpio.IN)
	time.sleep(0.1)


def reinisialiserMap():
	#mymap = []
	for x in range(0, lignes):
		vecteur = []
		for y in range(0, colonnes):
			vecteur.append(1)
		mymap.append(vecteur)

def afficherMap() :
	y = len(mymap)
	while(y > 0) :
		print mymap[y - 1]
		y = y -1

def callserver(url, params):
	r = requests.post(url, params=params, headers=headers)
	response =  r.json()
	print json.dumps(response) 
	return response

def verifierObstacle() :
	distance = ultrasonic.get_sample()
	if distance < DISTANCEOBSTACLE:
		return True
	else:
		return False

def getDistanceFromObstacle() :
	init()
	gpio.output(TRIG,1)
	#start = time.time()start = time.time()
	#print start
	time.sleep(0.00001)
	start = time.time()
	gpio.output(TRIG,0)
	print "avant la boucle"
	while gpio.input(ECHO) == 0:
	#	time.sleep(0.1)
	        pass
	#start = time.time()

	#while gpio.input(ECHO) == 1:
	#        pass
	#gpio.output(TRIG,0)
	stop = time.time()
	while gpio.input(ECHO) == 1:
		pass
	gpio.cleanup()

	distance=(stop-start)*17000
	print distance
	return distance

def tournerDroite() :
	init() 
	gpio.output(7, True)
	gpio.output(11, False)
	gpio.output(13, True)
	gpio.output(15, True)
	time.sleep(tf_droite)
	gpio.cleanup()
	time.sleep(DUREESLEEP)

def tournerGauche() :
	init()
	gpio.output(7, False)
	gpio.output(11, False)
	gpio.output(13, False)
	gpio.output(15, True)
	time.sleep(tf_gauche)
	gpio.cleanup()
	time.sleep(DUREESLEEP)

def avancer() :
	init()
	gpio.output(7, True)
	gpio.output(11, False)
	gpio.output(13, False)
	gpio.output(15, True)
	time.sleep(tf)
	gpio.cleanup()
	time.sleep(DUREESLEEP)

def reculer() :
	init()
	gpio.output(7, False)
	gpio.output(11, True)
	gpio.output(13, True)
	gpio.output(15, False)
	time.sleep(tf)
	gpio.cleanup()
	time.sleep(DUREESLEEP)

def getDistance(p1, p2):
	return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))

def runrobot():
	print "Thread lance"
	global DIRECTION
	global trajet
	global mymap
	global position
	global runrobot
	runrobot = False
	while True:
		if(runrobot):
			compteur = 0
			for point in trajet :
				print point
				if(compteur == 0):
					compteur = compteur+1
					continue
				if(runrobot == False):
					break
				while (DIRECTION != point[2]):
					if(point[2] - DIRECTION >= 0):
						DIRECTION = (DIRECTION + 1) % 4
						tournerDroite()
					else:
						DIRECTION = (DIRECTION - 1) % 4
						tournerGauche()
					
				avancer()
			runrobot = False
			print "------- Mission accomplie --------"
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
	print "9 : Recuperer donnee du serveur"
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



runinstruction()

while ch != 'q':
	global runrobot
	ch = getch()
	print "Execution de la tache demander"
	if ch == 'e':
	    avancer()
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
		lignes = int(chars[0])
		colonnes = int(chars[1])
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
		global trajet
		trajet = callserver(url_getTrajet, {})
		global mymap
		mymap = callserver(url_getMap, {})
		global lignes
		global colonnes
		lignes = len(mymap)
		colonnes = len(mymap[0])

