# Program to make NXT brick beep using NXT Python with Bluetooth socket
#
# Simon D. Levy  CSCI 250   Washington and Lee University    April 2011

# Change this ID to match the one on your brick.  You can find the ID by doing Settings / NXT Version.  
# You will have to put a colon between each pair of digits.
ID = '00:16:53:0C:CB:67'

import nxt.locator
import thread
from nxt.motor import *
# This is all we need to import for the beep, but you'll need more for motors, sensors, etc.
from nxt.bluesock import BlueSock
from time import sleep
from nxt.sensor import *


def play(note, b):
    if note:
        b.play_tone_and_wait(note, 500)
    else:
        sleep(0.5)

def spin_around(b):
    m_left = Motor(b, PORT_A)
    m_left.turn(100, 360)
    #m_right = Motor(b, PORT_B)
    #m_right.turn(-100, 360)
 
def turnmotor(m, power, degrees):
	m.turn(power, degrees)
	
#how long from start until the last instruction is ended
length = 30
    
# Create socket to NXT brick
sock = 	BlueSock(ID)

# On success, socket is non-empty
if sock:

   # Connect to brick
   brick = sock.connect()
   
   mx = Motor(brick, nxt.PORT_A)
   my = Motor(brick, nxt.PORT_B)
   motors = [mx, my]
   
   #Ultrasonic sensor latency test
   ultrasonic = Ultrasonic(brick, PORT_4)
   #ultrasonic.get_sample()
 
   # Play tone A above middle C for 1000 msec
   #brick.play_tone_and_wait(440, 1000)
   
  
   seconds = 0
   while 1:
	 distance = ultrasonic.get_sample()
	 print(("US val %d" % distance))
	 if distance < 50:
		 spin_around(brick)
	 else:
		 thread.start_new_thread(
			turnmotor,
			(motors[0], 80, 360))
		 thread.start_new_thread(
			turnmotor,
			(motors[1], 80, 360))
	 seconds = seconds + 1
	 if seconds >= length:
		break
	 time.sleep(1)
   # Close socket
   time.sleep(5)
   sock.close()

# Failure
else:
   print 'No NXT bricks found'


