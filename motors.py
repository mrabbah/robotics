import RPi.GPIO as gpio
import time

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setwarnings(False)
    #left motor
    gpio.setup(16, gpio.OUT)
    gpio.setup(18, gpio.OUT)
    #right motor
    gpio.setup(11, gpio.OUT)
    gpio.setup(13, gpio.OUT)

    gpio.setup(22, gpio.OUT)
    gpio.setup(15, gpio.OUT)

def move_direct(tf, direction):
    init()
    gpio.output(22, True)
    gpio.output(15, True)
    #left motor
    gpio.output(16, not direction)
    gpio.output(18, direction)
    #right motor
    gpio.output(11, direction)
    gpio.output(13, not direction)
    time.sleep(tf)
    gpio.cleanup()

print "Forward"
move_direct(4, True)
print "Backward"
move_direct(2, False)

