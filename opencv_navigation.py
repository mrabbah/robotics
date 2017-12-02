import sys
import tty, termios
import tty
import math
from time import sleep, time
import RPi.GPIO as GPIO
import numpy as np  # array library
import threading
import signal
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
import sys
from Queue import Queue
import imutils
from imutils.video import VideoStream
from imutils.video import FPS
import argparse

import cv2


##################################################
#            Navigation parameters               #
##################################################

duty_min = 15.0  # the minmum duty cycle to apply to motors bellow this value motors will not turn
duty_max = 40.0  # the maximum duty cycle to apply to motors (must not exceed 100)

v0 = 1.5  # The average velocity used by motors must be between 0 and 7.2

maxDistanceDetection = 40  # The maximum distance detected by the robot (US sensor)
minDistanceDetection = 5  # The minimum distance detected by the robot (US Sensor)


##################################################
#       Real time object detection part          #
##################################################

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
sleep(2.0)
fps = FPS().start()


class DetectionThread(threading.Thread):
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
        # loop over the frames from the video stream
        while not self.shutdown_flag.is_set():
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            # grab the frame dimensions and convert it to a blob
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                         0.007843, (300, 300), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()

            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > args["confidence"]:
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],
                                                 confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                                  COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

            # update the FPS counter
            fps.update()
            sleep(0.1)
        return


detection_thread = DetectionThread(name='detection_thread',
                                     args=('detection_thread',),
                                     kwargs={'id': 'detection_thread'})


def start_detection():
    # log.debug( "Starting navigation .... ")
    detection_thread.setDaemon(True)
    detection_thread.start()


def stop_detection():
    detection_thread.shutdown_flag.set()


##################################################
#                 Logging part                   #
##################################################

log = logging.getLogger('')
log.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s:(%(threadName)-10s) %(message)s')
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(format)
log.addHandler(sh)

fh = handlers.RotatingFileHandler("braitenberg_navigation_persist.log", maxBytes=(1048576*5), backupCount=7)
fh.setFormatter(format)
log.addHandler(fh)

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s:(%(threadName)-10s) %(message)s',datefmt='%m/%d/%Y %H:%M:%S',)


##################################################
#            Persisting data Part                #
##################################################

datas = Queue()
datas_file_path = 'braitenberg_navigation.csv'


class Data:
    def __init__(self, t, obtacles_distances, vl, vr):
        self.time = t
        self.obtacles_distances = obtacles_distances
        self.vl = vl
        self.vr = vr


def save_datas():
    log.debug('save data function called')
    global datas
    nb_lignes = datas.qsize()
    if nb_lignes > 0:
        log.debug("writing %d lines to %s files" % (nb_lignes, datas_file_path))
        outFile = open(datas_file_path, 'w')
        while datas.qsize():
            data = datas.get()
            line = '%f;' % data.time
            for obstacle_distance in data.obtacles_distances:
                line = line + '%f;' % obstacle_distance
            line = line + '%f;%f\n' % (data.vl, data.vr)
            outFile.write(line)
        outFile.flush()
        outFile.close()
    else:
        log.debug("no data to write to file")



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
        log.debug("Error : vl = %f must be between %f and %f" % (abs(vl), duty_min, duty_max))
        pwm_lm.ChangeDutyCycle(0)
    if abs(vr) >= duty_min and abs(vr) <= duty_max:
        pwm_rm.ChangeDutyCycle(abs(vr))
    else:
        log.debug("Error : vr = %f must be between %f and %f" % (abs(vr), duty_min, duty_max))
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
    # log.debug( "Starting Measurement...")
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
        # log.debug( "Thread running .... shutdown flag = %r " % self.shutdown_flag.is_set())
        step = 0
        t = time()
        while not self.shutdown_flag.is_set():
            distances_obstacles = [None] * 8
            positions = range(0, 8)
            if step % 2 == 1:
                positions = range(7, -1, -1)
            for x in positions:
                turn_to_angle(sensor_pos[x])
                sleep(0.1)
                distance = get_obstacle_distance()
                distances_obstacles[x] = distance
                # log.debug( "Distanc = %f \n" % distance)
                if distance > maxDistanceDetection:
                    sensor_val[x] = 0
                elif distance < minDistanceDetection:
                    sensor_val[x] = 1
                else:
                    sensor_val[x] = 1 - (
                        (distance - minDistanceDetection) / (maxDistanceDetection - minDistanceDetection))
                    # log.debug( "sensor_val[%d] = %f\n" % (x, sensor_val[x]))

            v_left = v0
            v_right = v0

            for i in range(0, 8):
                v_left = v_left + braitenbergL[i] * sensor_val[i]
                v_right = v_right + braitenbergR[i] * sensor_val[i]

            log.debug("step %d v left = %f and v right = %f\n\t" % (step, v_left, v_right))

            v_left = v_left * duty_max / v0
            v_right = v_right * duty_max / v0

            t_prime = time()
            data = Data(t_prime - t, distances_obstacles, v_left, v_right)
            datas.put(data)
            # log.debug( "step %d , v left = %f and v right = %f\n\t" % (step, v_left, v_right))

            change_velocity(v_left, v_right)
            # sleep(0.1)
            step = step + 1
        sleep(1)
        return


navigation_thread = NavigationThread(name='navigation_thread',
                                     args=('navigation_thread',),
                                     kwargs={'id': 'navigation_thread'})


def start_navigation():
    # log.debug( "Starting navigation .... ")
    navigation_thread.setDaemon(True)
    navigation_thread.start()


def stop_navigation():
    navigation_thread.shutdown_flag.set()
    log.debug('calling save data from stop navigation')
    if navigation_thread.isAlive():
        navigation_thread.join() # wait until thread terminate
    save_datas()


def service_shutdown(signum, frame):
    stop_navigation()
    stop_detection()
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
    print "4 : Start detection"
    print "5 : Stop detection"
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
    log.debug("Executing requested task ... %s " % ch)
    if ch == '1':
        start_navigation()
    elif ch == '2':
        stop_navigation()
    elif ch == '3':
        get_obstacle_distance()
    elif ch == '4':
        start_detection()
    elif ch == '5':
        stop_detection()
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

stop_detection()
# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
