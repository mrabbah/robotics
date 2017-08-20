import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)

TRIG = 29
ECHO = 31

gpio.setup(TRIG, gpio.OUT)
gpio.setup(TRIG, 0)

gpio.setup(ECHO, gpio.IN)

time.sleep(0.1)

print "Starting Measurement..."

gpio.output(TRIG, 1)
time.sleep(0.00001)
gpio.output(TRIG, 0)

while gpio.input(ECHO) == 0 :
    pass

start = time.time()

while gpio.input(ECHO) == 1 :
    pass

stop = time.time()

distance = (stop - start) * 17000 

print "Distance = %f cm" % distance

gpio.cleanup() 
