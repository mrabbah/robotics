import sys
import tty, termios
import tty
import math
from time import sleep, time
import RPi.GPIO as GPIO
import numpy as np  # array library
import threading
import signal


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
#                OpenCV Part                #
##################################################


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
