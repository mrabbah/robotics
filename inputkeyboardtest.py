
import sys
import tty, termios
import tty
import math




def getch() :
	print "Quelle action voulez vous faire?"
	print "1 : Entrer les coordonnees de depart"
	print "2 : Entrer les coordonnees d arrive"
	print "3 : Entrer la dimension de la carte"
	print "4 : Lancer le robot"
	print "5 : Arreter le robot"
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
pdd = [0,0]
pa = [1, 1]

def getDistance(p1, p2):
	return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))

print getDistance(pdd, pa)

while ch != 'q':
	ch = getch()
	print "Execution de la tache demander"
	if ch == '1':
		line = sys.stdin.readline()
		print line
		chars = line.split(',')
		pdd[0] = int(chars[0])
		pdd[1] = int(chars[1])


	elif ch == '2':
		line = sys.stdin.readline()
	elif ch == '3':
		line = sys.stdin.readline()
	elif ch == '4':
		runrobot = True
	elif ch == '5':
		runrobot = False
