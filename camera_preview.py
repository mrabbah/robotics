from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
print "camera start preview"
sleep(10)
camera.stop_preview()
print "camera stoped preview"

