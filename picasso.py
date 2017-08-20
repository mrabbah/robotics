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

# KNOWN_DISTANCE = {}

focalLengths = {}

ROTATION = 90
ROTATION_TRIANGLE = 60
ROTATION_CERCLE = 360
ROTATION_STYLO = 15

PUISSANCE = 80
DD = 100
MAXDISTANCEVIEW = 50
MINSHAPCONSIDIRE = 500
PRECISIONFORM = 0.015
DUREEATTENTECAM = 8
DV = 360

def getch():
    print "Quelle action voulez vous faire?"
    print "1 : Dessiner cercle"
    print "2 : Dessiner triangle"
    print "3 : Dessiner caree"
    print "4 : Detecter forme"
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

# fin all the 'red shapes in the image'
lowerRed2 = np.array([160, 100, 100], np.uint8)
upperRed2 = np.array([179, 255, 255], np.uint8)
lowerRed1 = np.array([0, 100, 100], np.uint8)
upperRed1 = np.array([10, 255, 255], np.uint8)


def getShapeColorFromImage(image):
    # appliquer filtre pour enlever les parasites de l image
    median = cv2.medianBlur(image, 9)
    hsv_img = cv2.cvtColor(median, cv2.COLOR_BGR2HSV)

    shapeMask1 = cv2.inRange(hsv_img, lowerRed1, upperRed1)
    shapeMask2 = cv2.inRange(hsv_img, lowerRed2, upperRed2)

    shapeMask = cv2.addWeighted(shapeMask1, 1.0, shapeMask2, 1.0, 0.0)

    # find contours in the thresholded image and initialize the
    # shape detector
    cnts, hierarchy = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

    print "I found %d  shapes" % (len(cnts))

    # cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    sd = ShapeDetector()
    # loop over the contours
    for c in cnts:
        ca = cv2.contourArea(c)
        if ca > MINSHAPCONSIDIRE:
            print "ca =  %d " % (ca)

            shape = sd.detect(c)
            print shape
            return shape
    return None


def getImageFromCam():
    cap = cv2.VideoCapture(-1)
    # cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, int(352))
    # cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, int(288))
    # cap.set(cv2.cv.CV_CAP_PROP_FPS,5)
    ret, frame = cap.read()
    del (cap)
    return frame

def descendre_stylo(pick):
    #TODO PRECISER LA VALEUR
    pick.turn(ROTATION_STYLO, 69, False)
def remonter_stylo(pick):
    # TODO PRECISER LA VALEUR
    pick.turn(-1 * ROTATION_STYLO, 69, False)

def dessiner_cercle(both, rightboth, pick):
    descendre_stylo(pick)
    rightboth.turn(PUISSANCE, ROTATION_CERCLE, False)
    remonter_stylo(pick)

def dessiner_triangle(both, rightboth, pick):
    descendre_stylo(pick)
    both.turn(PUISSANCE, DD, False)
    rightboth.turn(PUISSANCE, ROTATION_TRIANGLE, False)
    both.turn(PUISSANCE, DD, False)
    rightboth.turn(PUISSANCE, ROTATION_TRIANGLE, False)
    both.turn(PUISSANCE, DD, False)
    remonter_stylo(pick)

def dessiner_carre(both, rightboth, pick):
    descendre_stylo(pick)
    both.turn(PUISSANCE, DD, False)
    rightboth.turn(PUISSANCE, ROTATION, False)
    both.turn(PUISSANCE, DD, False)
    rightboth.turn(PUISSANCE, ROTATION, False)
    both.turn(PUISSANCE, DD, False)
    rightboth.turn(PUISSANCE, ROTATION, False)
    both.turn(PUISSANCE, DD, False)
    remonter_stylo(pick)

sock = BlueSock(ID)
if sock:
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
            both.turn(-1 * PUISSANCE, DD, False)
        elif ch == 's':
            leftboth.turn(PUISSANCE, ROTATION, False)
        elif ch == 'f':
            rightboth.turn(PUISSANCE, ROTATION, False)
        elif ch == '1':
            dessiner_cercle(both, rightboth, pick)
        elif ch == '2':
            dessiner_triangle(both, rightboth, pick)
        elif ch == '3':
            dessiner_carre(both, rightboth, pick)
        elif ch == '4':
            #TODO SE DEPLACER VERS LA FORME
            image = getImageFromCam()
            form = getShapeColorFromImage(image)
            print form
            #TODO ALLER VERS ZONE DESSIN
            if form == 'circle':
                dessiner_cercle(both, rightboth, pick)
            elif form == 'rectangle':
                dessiner_carre(both, rightboth, pick)
            else:
                dessiner_triangle(both, rightboth, pick)


    sock.close()
