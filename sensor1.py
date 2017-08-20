import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
#GPIO.cleanup()
TRIG = 12
ECHO = 16
GPIO.setwarnings(False)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.output(TRIG,0)

GPIO.setup(ECHO,GPIO.IN)

time.sleep(0.1)

print "starting Measurement..."
#GPIO.output(TRIG,0)
GPIO.output(TRIG,1)
#start = time.time()start = time.time()
#print start
time.sleep(0.00001)
start = time.time()
GPIO.output(TRIG,0)
print "avant la boucle"
while GPIO.input(ECHO) == 0:
#	time.sleep(0.1)
        pass
#start = time.time()

#while GPIO.input(ECHO) == 1:
#        pass
#GPIO.output(TRIG,0)
stop = time.time()
while GPIO.input(ECHO) == 1:
	pass
GPIO.cleanup()

distance=(stop-start)*17000

print(distance)

#GPIO.cleanup()
