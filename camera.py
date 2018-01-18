import cv2
from pivideostream import PiVideoStream
import imutils
import time

class VideoCamera(object):
    def __init__(self, resolution=(320,240), framerate=32):
        self.vs = PiVideoStream(resolution,framerate).start()
        time.sleep(2.0)
        
    def hflip(self,hflip=True):
        self.vs.hflip(hflip)
        
    def vflip(self,vflip=True):
        self.vs.vflip(vflip)
        
    def exposure_mode(self,exposure_mode="auto"):
        self.vs.exposure_mode(exposure_mode)

    def shutter_speed(self,speed):
        self.vs.shutter_speed(speed)

    def reset_resolution_framerate(self,resolution=(320,240),framerate=32):
        self.vs.stop()
        time.sleep(1.0)
        self.vs = PiVideoStream(resolution,framerate).start()
        self.vs.shutter_speed((1/framerate)*1000000)
        time.sleep(1.0)

    def __del__(self):
        self.vs.stop()

    def get_frame(self):
        frame = self.vs.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_object(self, classifier):
        found_objects = False
        frame = self.vs.read().copy() 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(objects) > 0:
            found_objects = True

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)


