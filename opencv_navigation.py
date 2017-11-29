import sys
import tty, termios
import tty
import math
from time import sleep, time
import RPi.GPIO as GPIO
import numpy as np  # array library
import threading
import signal
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
from colorama import init,Fore

##################################################
#            Navigation parameters               #
##################################################

duty_min = 15.0  # the minmum duty cycle to apply to motors bellow this value motors will not turn
duty_max = 40.0  # the maximum duty cycle to apply to motors (must not exceed 100)

v0 = 1.5  # The average velocity used by motors must be between 0 and 7.2



##################################################
#                   Motors Part                  #
##################################################

GPIO.setmode(GPIO.BOARD)
# gpio.setwarnings(False)

# left motor
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
pwm_lm = GPIO.PWM(22, 100)
pwm_lm.start(20)

# right motor
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
pwm_rm = GPIO.PWM(15, 100)
pwm_rm.start(20)


def stop_motors():
    sleep(0.1)
    GPIO.output(16, False)
    GPIO.output(18, False)
    GPIO.output(11, False)
    GPIO.output(13, False)


def forward():
    # left motor
    GPIO.output(16, False)
    GPIO.output(18, True)
    # right motor
    GPIO.output(11, True)
    GPIO.output(13, False)
    # pwm_lm.ChangeDutyCycle(70)
    # pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def backward():
    # left motor
    GPIO.output(16, True)
    GPIO.output(18, False)
    # right motor
    GPIO.output(11, False)
    GPIO.output(13, True)
    # pwm_lm.ChangeDutyCycle(70)
    # pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def turn_left():
    # left motor
    GPIO.output(16, True)
    GPIO.output(18, False)
    # right motor
    GPIO.output(11, True)
    GPIO.output(13, False)
    # pwm_lm.ChangeDutyCycle(70)
    # pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def turn_right():
    # left motor
    GPIO.output(16, False)
    GPIO.output(18, True)
    # right motor
    GPIO.output(11, False)
    GPIO.output(13, True)
    # pwm_lm.ChangeDutyCycle(70)
    # pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def change_velocity(vl, vr):
    # left motor
    GPIO.output(16, not (vl > 0))
    GPIO.output(18, (vl > 0))
    # right motor
    GPIO.output(11, (vr > 0))
    GPIO.output(13, not (vr > 0))
    if abs(vl) >= duty_min and abs(vl) <= duty_max:  # Protect motors
        pwm_lm.ChangeDutyCycle(abs(vl))
    else:
        print "Error : vl = %f must be between %f and %f" % (abs(vl), duty_min, duty_max)
        pwm_lm.ChangeDutyCycle(0)
    if abs(vr) >= duty_min  and abs(vr) <= duty_max:
        pwm_rm.ChangeDutyCycle(abs(vr))
    else:
        print "Error : vr = %f must be between %f and %f" % (abs(vr), duty_min, duty_max)
        pwm_rm.ChangeDutyCycle(0)
    stop_motors()


##################################################
#                  OpenCV Part                   #
##################################################
# initialize the camera and grab a reference to the raw camera capture
DisplayImage = True

print "Starting OpenCV"
capture = cv2.VideoCapture(0)

capture.set(3, 640)  # 1024 640 1280 800 384
capture.set(4, 480)  # 600 480 960 600 288

if DisplayImage is True:
    cv2.namedWindow("camera", 0)
    cv2.namedWindow("transform", 0)
    print (Fore.GREEN + "Creating OpenCV windows")
    # cv2.waitKey(50)
    cv2.resizeWindow("camera", 640, 480)
    cv2.resizeWindow("transform", 300, 300)
    print (Fore.GREEN + "Resizing OpenCV windows")
    # cv2.waitKey(50)
    cv2.moveWindow("camera", 400, 30)
    cv2.moveWindow("transform", 1100, 30)
    print (Fore.GREEN + "Moving OpenCV window")
    cv2.waitKey(50)

##################################################################################################
#
# Display image - Capture a frame and display it on the screen
#
##################################################################################################
def DisplayFrame():
    ret, img = capture.read()
    ret, img = capture.read()
    ret, img = capture.read()
    ret, img = capture.read()
    ret, img = capture.read()  # get a bunch of frames to make sure current frame is the most recent

    cv2.imshow("camera", img)
    cv2.waitKey(10)


##################################################################################################
#
# Reform Contours - Takes an approximated array of 4 pairs of coordinates and puts them in the order
# TOP-LEFT, TOP-RIGHT, BOTTOM-RIGHT, BOTTOM-LEFT
#
##################################################################################################
def ReformContours(contours):
    contours = contours.reshape((4, 2))
    contoursnew = np.zeros((4, 2), dtype=np.float32)

    add = contours.sum(1)
    contoursnew[0] = contours[np.argmin(add)]
    contoursnew[2] = contours[np.argmax(add)]

    diff = np.diff(contours, axis=1)
    contoursnew[1] = contours[np.argmin(diff)]
    contoursnew[3] = contours[np.argmax(diff)]

    return contoursnew

##################################################################################################
#
# Check Ground
#
##################################################################################################

def CheckGround():
    StepSize = 8
    EdgeArray = []

    sleep(0.1)  # let image settle
    ret, img = capture.read()  # get a bunch of frames to make sure current frame is the most recent
    ret, img = capture.read()
    ret, img = capture.read()
    ret, img = capture.read()
    ret, img = capture.read()  # 5 seems to be enough

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert img to grayscale and store result in imgGray
    imgGray = cv2.bilateralFilter(imgGray, 9, 30, 30)  # blur the image slightly to remove noise
    imgEdge = cv2.Canny(imgGray, 50, 100)  # edge detection

    imagewidth = imgEdge.shape[1] - 1
    imageheight = imgEdge.shape[0] - 1

    for j in range(0, imagewidth, StepSize):  # for the width of image array
        for i in range(imageheight - 5, 0, -1):  # step through every pixel in height of array from bottom to top
            # Ignore first couple of pixels as may trigger due to undistort
            if imgEdge.item(i, j) == 255:  # check to see if the pixel is white which indicates an edge has been found
                EdgeArray.append((j, i))  # if it is, add x,y coordinates to ObstacleArray
                break  # if white pixel is found, skip rest of pixels in column
        else:  # no white pixel found
            EdgeArray.append(
                (j, 0))  # if nothing found, assume no obstacle. Set pixel position way off the screen to indicate
            # no obstacle detected

    for x in range(len(EdgeArray) - 1):  # draw lines between points in ObstacleArray
        cv2.line(img, EdgeArray[x], EdgeArray[x + 1], (0, 255, 0), 1)
    for x in range(len(EdgeArray)):  # draw lines from bottom of the screen to points in ObstacleArray
        cv2.line(img, (x * StepSize, imageheight), EdgeArray[x], (0, 255, 0), 1)

    if DisplayImage is True:
        cv2.imshow("camera", img)
        cv2.waitKey(10)


##################################################################################################
#
# NewMap - Creates a new map
#
##################################################################################################

def NewMap(MapWidth, MapHeight):
    MapArray = np.ones((MapHeight, MapWidth, 3), np.uint8)
    MapArray[:MapWidth] = (255, 255, 255)  # (B, G, R)

    return MapArray


##################################################################################################
#
# AddToMap -
#
##################################################################################################

def AddToMap(MapArray, X, Y, Type):
    Width = MapArray.shape[1]
    Height = MapArray.shape[0]
    print Type, "in AddToMap"

    if Type == 'FOOD':
        cv2.circle(MapArray, (X, Y), 2, (0, 0, 255), -1)  # draw a circle
    elif Type == 'HOME':
        cv2.circle(MapArray, (X, Y), 2, (0, 255, 0), -1)  # draw a circle

    return MapArray


##################################################################################################
#
# ShowMap - Displays a map in an opencv window
# MapArray is a numpy array where each element has a value between 0 and 1
#
##################################################################################################

def ShowMap(MapArray):
    cv2.imshow("map", MapArray)
    cv2.waitKey(50)


def destroy():
    cv2.destroyAllWindows()


class NavigationThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        self.shutdown_flag = threading.Event()
        return

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        #print "Thread running .... shutdown flag = %r " % self.shutdown_flag.is_set()
        step = 0
        '''
        while not self.shutdown_flag.is_set():
            positions = range(0, 8)

            v_left = v0
            v_right = v0

            print "step %d v left = %f and v right = %f\n\t" % (step, v_left, v_right)

            v_left = v_left * duty_max / v0
            v_right = v_right * duty_max / v0

            print "step %d , v left = %f and v right = %f\n\t" % (step, v_left, v_right)

            change_velocity(v_left, v_right)
            # sleep(0.1)
            step = step + 1
        sleep(1)
        '''
        return


navigation_thread = NavigationThread(name='navigation_thread',
                                     args=('navigation_thread',),
                                     kwargs={'id': 'navigation_thread'})


def start_navigation():
    #print "Starting navigation .... "
    navigation_thread.setDaemon(True)
    navigation_thread.start()


def stop_navigation():
    navigation_thread.shutdown_flag.set()


def service_shutdown(signum, frame):
    stop_navigation()
    pwm_lm.stop()
    pwm_rm.stop()
    GPIO.cleanup()

##################################################
#             Main application logic             #
##################################################


def get_ch():
    print "Which action you want?"
    print "1 : Start navigation"
    print "2 : Stop navigation"
    print "e : Go forward"
    print "d : Backward"
    print "f : Turn right"
    print "s : Turn left"
    print "q : Quit"

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        choice = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return choice


ch = ' '
signal.signal(signal.SIGTERM, service_shutdown)
print "Ready"

while ch != 'q' and ch != 'Q':
    ch = get_ch()
    print "Executing requested task ... %s " % ch
    if ch == '1':
        start_navigation()
    elif ch == '2':
        stop_navigation()
    elif ch == 'e' or ch == 'E':
        forward()
    elif ch == 'd' or ch == 'D':
        backward()
    elif ch == 'f' or ch == 'F':
        turn_right()
    elif ch == 's' or ch == 'S':
        turn_left()

# Cleaning App
stop_navigation()
pwm_lm.stop()
pwm_rm.stop()
GPIO.cleanup()
