import RPi.GPIO as gpio
import time

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setwarnings(False)
    gpio.setup(12, gpio.OUT)


def turn_right():
    nb=0
    while nb  < 10:
        gpio.output(12, False)
        time.sleep(0.015)
        gpio.output(12, True)
        time.sleep(0.005)
        nb = nb + 1


#def turn_left():
#    nb=0
#    while nb  < 10:
#        gpio.output(12, False)
#        time.sleep(0.005)
#        gpio.output(12, True)
#        time.sleep(0.015)
#        nb = nb + 1

init()
#turn_left()
#turn_left()
turn_right()

gpio.cleanup()
