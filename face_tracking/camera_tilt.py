import time
import picamera
import math

import pantilthat



camera = picamera.PiCamera()
camera.rotation = 180
try:
    camera.start_preview()
    pantilthat.pan(-20)
    while True:
        # Get the time in seconds
        t = time.time()

        # G enerate an angle using a sine wave (-1 to 1) multiplied by 90 (-90 to 90)
        a = math.sin(t * 0.3) * 90
        
        # Cast a to int for v0.0.2
        a = int(a)

        pantilthat.tilt(a)
        #pantilthat.tilt(a)

        # Two decimal places is quite enough!
        print(round(a,2))

        # Sleep for a bit so we're not hammering the HAT with updates
        time.sleep(0.005)
    camera.stop_preview()
finally:
    camera.close()