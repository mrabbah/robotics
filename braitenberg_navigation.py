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

maxDistanceDetection = 40  # The maximum distance detected by the robot (US sensor)
minDistanceDetection = 5  # The minimum distance detected by the robot (US Sensor)

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
    # print "Starting Measurement..."
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


turn_to_angle(sensor_pos[3])

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
            if step % 2 == 1:
                positions = range(7, -1, -1)
            for x in positions:
                turn_to_angle(sensor_pos[x])
                sleep(0.1)
                distance = get_obstacle_distance()
                # print "Distanc = %f \n" % distance
                if distance > maxDistanceDetection:
                    sensor_val[x] = 0
                elif distance < minDistanceDetection:
                    sensor_val[x] = 1
                else:
                    sensor_val[x] = 1 - (
                        (distance - minDistanceDetection) / (maxDistanceDetection - minDistanceDetection))
                # print "sensor_val[%d] = %f\n" % (x, sensor_val[x])

            v_left = v0
            v_right = v0

            for i in range(0, 8):
                v_left = v_left + braitenbergL[i] * sensor_val[i]
                v_right = v_right + braitenbergR[i] * sensor_val[i]

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
signal.signal(signal.SIGTERM, service_shutdown)
print "Ready"

while ch != 'q' and ch != 'Q':
    ch = get_ch()
    print "Executing requested task ... %s " % ch
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
stop_navigation()
turn_to_angle(sensor_pos[3])
pwm_lm.stop()
pwm_rm.stop()
GPIO.cleanup()
