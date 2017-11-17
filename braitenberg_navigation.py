import sys
import tty, termios
import tty
import math
from time import sleep, time
import RPi.GPIO as GPIO
import numpy as np  # array library

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
    GPIO.output(16, False)
    GPIO.output(18, True)
    # right motor
    GPIO.output(11, False)
    GPIO.output(13, True)
    pwm_lm.ChangeDutyCycle(vl)
    pwm_rm.ChangeDutyCycle(vr)
    stop_motors()


##################################################
#                Servo motor Part                #
##################################################

GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 100)
pwm.start(5)


def turn_to_angle(angle):
    duty = (float(angle) + 35) / 10.0 + 2.5
    pwm.ChangeDutyCycle(duty)


##################################################
#             Ultrasonic sensor Part             #
##################################################

TRIG = 29
ECHO = 31

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(TRIG, 0)

GPIO.setup(ECHO, GPIO.IN)

sleep(0.1)


def get_obstacle_distance():
    """
    This function give the distance in cm
    :return: the distance from obstacle in cm
    """
    print "Starting Measurement..."
    GPIO.output(TRIG, 1)
    sleep(0.00001)
    GPIO.output(TRIG, 0)
    while GPIO.input(ECHO) == 0:
        pass

    start = time()

    while GPIO.input(ECHO) == 1:
        pass

    stop = time()

    distance = (stop - start) * 17000

    return distance


##################################################
#                Braitenberg Part                #
##################################################

sensor_val = [None] * 8  # empty array for sensor measurements

PI = math.pi  # pi=3.14..., constant
ar = 180.0 / 7.0  # Rotation angle we simulate 8 US sensors in front

sensor_pos = np.array([0.0, ar, ar * 2.0, ar * 3.0, ar * 4.0, ar * 5.0, ar * 6.0, 180.0])

braitenbergL = [-0.2, -0.4, -0.6, -0.8, -1, -1.2, -1.4, -1.6]
braitenbergR = [-1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2]

v0 = 70
maxDistanceDetection = 500
minDistanceDetection = 2


def start_navigation():
    for x in range(0, 8):
        turn_to_angle(sensor_pos[x])
        distance = get_obstacle_distance()
        if distance > maxDistanceDetection or distance < minDistanceDetection:
            sensor_val[x] = 0
        else:
            sensor_val[x] = 1 - ((distance - minDistanceDetection) / (maxDistanceDetection - minDistanceDetection))

    for i in range(0, 8):
        vLeft = vLeft + braitenbergL[i] * sensor_val[i]
        vRight = vRight + braitenbergR[i] * sensor_val[i]

    change_velocity(vLeft, vRight)


def stop_navigation():
    pass


##################################################
#             Main application logic             #
##################################################


def get_ch():
    print "Which action you want?"
    print "1 : Start navigation"
    print "2 : Stop navigation"
    print "3 : Get obstacle distance"
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
print "Ready"

while ch != 'q' and ch != 'Q':
    ch = get_ch()
    # print "Executing requested task ..."
    if ch == '1':
        start_navigation()
    elif ch == '2':
        stop_navigation()
    elif ch == '3':
        get_obstacle_distance()
    elif ch == 'e' or ch == 'E':
        forward()
    elif ch == 'd' or ch == 'D':
        backward()
    elif ch == 'f' or ch == 'F':
        turn_right()
    elif ch == 's' or ch == 'S':
        turn_left()

# Cleaning App

pwm_lm.stop()
pwm_rm.stop()
GPIO.cleanup()
