from picamera import PiCamera, Color
from time import sleep

camera = PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = 15
camera.annotate_text = "Hello world"
camera.annotate_text_size = 160
camera.annotate_background = Color('blue')
camera.annotate_foreground = Color('yellow')
camera.start_preview()
camera.brightness = 50
camera.contrast = 50
camera.image_effect = 'none'
camera.awb_mode = 'auto'
camera.exposure_mode = 'night'
sleep(5)
camera.capture('/home/pi/Desktop/max4.jpg')
camera.stop_preview()

