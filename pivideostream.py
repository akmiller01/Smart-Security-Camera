# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
from numpy import zeros

class PiVideoStream:
	def __init__(self, resolution=(320, 240), framerate=32):
		# initialize the camera and stream
		self.frame = zeros(resolution)
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False
		
	def hflip(self,hflip=True):
		self.camera.hflip = hflip
		
	def vflip(self,vflip=True):
		self.camera.vflip = vflip
		
	def exposure_mode(self,exposure_mode="auto"):
		self.camera.exposure_mode = exposure_mode
		
	def iso(self,iso=0):
		self.camera.iso = iso

	def shutter_speed(self,speed):
		if speed<=(1/self.camera.framerate)*1000000:
			self.camera.shutter_speed = speed
		else:
			self.camera.shutter_speed = (1/self.camera.framerate)*1000000
		
	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rawCapture.truncate(0)

			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recent
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
