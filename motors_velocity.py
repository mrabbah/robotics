import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)
#gpio.setwarnings(False)

#left motor
gpio.setup(16, gpio.OUT)
gpio.setup(18, gpio.OUT)
gpio.setup(22, gpio.OUT)
pwm_lm = gpio.PWM(22, 100)
pwm_lm.start(20)    

#right motor
gpio.setup(11, gpio.OUT)
gpio.setup(13, gpio.OUT)
gpio.setup(15, gpio.OUT)
pwm_rm = gpio.PWM(15, 100)
pwm_rm.start(20)

#left motor
gpio.output(16, False)
gpio.output(18, True)

#right motor
gpio.output(11, True)
gpio.output(13, False)

time.sleep(2)
pwm_lm.ChangeDutyCycle(70) 
pwm_rm.ChangeDutyCycle(10) 

time.sleep(4)
pwm_lm.stop()
pwm_rm.stop()
gpio.cleanup()


