import sys
import tty, termios
import tty
import math
from picamera import PiCamera
from time import sleep
import RPi.GPIO as gpio

##################################################
#                   Camera Part                  #
##################################################

camera = PiCamera()
camera.resolution = (1024, 768) # (640, 480)
camera.framerate = 15
camera.brightness = 40
camera.contrast = 60
# camera.image_effect = 'none'
camera.awb_mode = 'sunlight'
camera.sensor_mode = 4
# camera.exposure_mode = 'night'

camera.start_preview()
sleep(2)
def record_video():
    print "starting recording"
    # camera.start_preview()
    camera.start_recording('/home/pi/Desktop/video.h264')
    camera.wait_recording()


def stop_recording():
    camera.stop_recording()
    # camera.stop_preview()
    print "record stopped video is located at /home/pi/Desktop/video.h264"


def shoot():
    print "taking picture"
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/Desktop/image.jpg')
    camera.stop_preview()
    print "picture toked and is located at /home/pi/Desktop/image.jpg"


##################################################
#                   Motors Part                  #
##################################################

gpio.setmode(gpio.BOARD)
# gpio.setwarnings(False)

# left motor
gpio.setup(16, gpio.OUT)
gpio.setup(18, gpio.OUT)
gpio.setup(22, gpio.OUT)
pwm_lm = gpio.PWM(22, 100)
pwm_lm.start(20)

# right motor
gpio.setup(11, gpio.OUT)
gpio.setup(13, gpio.OUT)
gpio.setup(15, gpio.OUT)
pwm_rm = gpio.PWM(15, 100)
pwm_rm.start(20)

def stop_motors():
    sleep(0.1)
    gpio.output(16, False)
    gpio.output(18, False)
    gpio.output(11, False)
    gpio.output(13, False)

def forward():
    # left motor
    gpio.output(16, False)
    gpio.output(18, True)
    # right motor
    gpio.output(11, True)
    gpio.output(13, False)
    #pwm_lm.ChangeDutyCycle(70)
    #pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def backward():
    # left motor
    gpio.output(16, True)
    gpio.output(18, False)
    # right motor
    gpio.output(11, False)
    gpio.output(13, True)
    #pwm_lm.ChangeDutyCycle(70)
    #pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def turn_left():
    # left motor
    gpio.output(16, True)
    gpio.output(18, False)
    # right motor
    gpio.output(11, True)
    gpio.output(13, False)
    #pwm_lm.ChangeDutyCycle(70)
    #pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def turn_right():
    # left motor
    gpio.output(16, False)
    gpio.output(18, True)
    # right motor
    gpio.output(11, False)
    gpio.output(13, True)
    # pwm_lm.ChangeDutyCycle(70)
    # pwm_rm.ChangeDutyCycle(70)
    stop_motors()


def get_obstacle_distance():
    pass


def get_ch():
    print "Which action you want?"
    print "1 : Start video recording"
    print "2 : Stop video recording"
    print "3 : Take picture"
    print "4 : Get obstacle distance"
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
        record_video()
    elif ch == '2':
        stop_recording()
    elif ch == '3':
        shoot()
    elif ch == '4':
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

camera.stop_preview()
camera.close()
pwm_lm.stop()
pwm_rm.stop()
gpio.cleanup()
