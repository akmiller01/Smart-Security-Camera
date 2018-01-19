import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
import time
import threading
from localtime import LocalTime

email_update_interval = 600 # sends an email only once in this time interval
lt = LocalTime('Baltimore')
if lt.is_night():
	fr = 1
	speed = (1/fr)*1000000
	mode = " (night mode)"
	em = "night"
else:
	fr = 16
	speed = 0
	mode = " (day mode)"
	em = "auto"
video_camera = VideoCamera(resolution=(640,480),framerate=fr) # creates a camera object, flip vertically
video_camera.shutter_speed(speed)
video_camera.hflip()
video_camera.vflip()
video_camera.exposure_mode(em)
# object_classifier = cv2.CascadeClassifier("models/fullbody_recognition_model.xml") # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
last_epoch = 0

def check_for_objects():
	global last_epoch
	while True:
		pass
#		try:
#			frame, found_obj = video_camera.get_object(object_classifier)
#			if found_obj and (time.time() - last_epoch) > email_update_interval:
#				last_epoch = time.time()
#				print "Sending email..."
#				# sendEmail(frame)
#				print "done!"
#		except:
#			print "Error sending email: ", sys.exc_info()[0]

@app.route('/')
def index():
    return render_template('index.html',mode=mode)

def gen(camera):
    while True:
        frame = camera.get_frame()
	if frame is None:
		continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False, threaded=True)
