import cv2
from pivideostream import PiVideoStream
import imutils
import time
import json
from localtime import LocalTime
import numpy as np

class VideoCamera(object):
    def __init__(self, resolution=(320,240), framerate=32):
        self.conf = json.load(open("conf.json"))
        self.lt = LocalTime("Baltimore")
        self.avg = None
        self.avg_count = 0
        self.motionCounter = 0
        self.motion_frames = []
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.contour_area = 0
        self.vs = PiVideoStream(resolution,framerate).start()
        time.sleep(self.conf["camera_warmup_time"])
        
    def hflip(self,hflip=True):
        self.vs.hflip(hflip)
        
    def vflip(self,vflip=True):
        self.vs.vflip(vflip)
        
    def exposure_mode(self,exposure_mode="auto"):
        self.vs.exposure_mode(exposure_mode)

    def iso(self,iso=0):
        self.vs.iso(iso)

    def shutter_speed(self,speed):
        self.vs.shutter_speed(speed)

    def change_framerate(self,framerate=32):
        self.vs.stop(stop_camera=False)
        time.sleep(self.conf["camera_cooldown_time"])
        self.vs.camera.framerate = framerate
        self.vs.shutter_speed(0)
        self.vs.start()
        time.sleep(self.conf["camera_warmup_time"])
        self.avg_count = 0

    def __del__(self):
        self.vs.stop(stop_camera=True)

    def get_frame(self):
        frame = self.vs.read().copy()
        framerate = self.vs.camera.framerate
        # draw the text and timestamp on the frame
        timestamp = self.lt.now()
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
        cv2.putText(frame, "FPS: {}; Contour area: {}".format(framerate,self.contour_area), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if self.w>0:
            cv2.rectangle(frame, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), 2)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_object(self):
        frame = self.vs.read().copy()
        timestamp = self.lt.now()
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        found_obj = False
        
        frame = imutils.resize(frame,width=500)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(21,21),0)
        
        if self.avg is None or self.avg_count < self.conf["camera_adjustment_frames"]:
            self.avg = gray.copy().astype("float")
            self.avg_count += 1
            if self.avg_count == self.conf["camera_adjustment_frames"]:
                print("[INFO] motion detector live...")
            return (None, False)
        
        cv2.accumulateWeighted(gray,self.avg,0.5)
        frameDelta = cv2.absdiff(gray,cv2.convertScaleAbs(self.avg))
        
        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, self.conf["delta_thresh"], 255,cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            self.contour_area = cv2.contourArea(c)
            if cv2.contourArea(c) < self.conf["min_area"]:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update found_obj
            (self.x, self.y, self.w, self.h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), 2)
            found_obj = True
        
        # check to see if the room is occupied
        if found_obj:
            print("[INFO] found object!")
            # increment the motion counter
            self.motionCounter += 1
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
            self.motion_frames.append(frame)

            # check to see if the number of frames with consistent motion is
            # high enough
            if self.motionCounter >= self.conf["min_motion_frames"]:
                print("[INFO] occupied!")
                self.motionCounter = 0
                vis = np.concatenate(self.motion_frames,axis=0)
                return (vis, found_obj)
            
            return (None, False)

        # otherwise, the room is not occupied
        else:
            (self.x, self.y, self.w, self.h) = (0,0,0,0)
            self.motionCounter = 0
            self.motion_frames = []
            return (None, False)


