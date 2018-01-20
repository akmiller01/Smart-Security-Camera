import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
import time
import threading
from localtime import LocalTime

email_update_interval = 600 # sends an email only once in this time interval
save_update_interval = 60 #Save once per minute
camera_settings = {
        "night":{
                "fr":1,
                "speed":1000000,
                "ex":"night",
                "iso":800
        },
        "day":{
                "fr":16,
                "speed":0,
                "ex":"auto",
                "iso":0
        }
}
lt = LocalTime('Baltimore')
current_state = lt.current_state()
camera_mode = camera_settings[current_state]
video_camera = VideoCamera(resolution=(640,480),framerate=camera_mode["fr"]) # creates a camera object, flip vertically
video_camera.shutter_speed(camera_mode["speed"])
video_camera.hflip()
video_camera.vflip()
video_camera.iso(camera_mode["iso"])

# App Globals (do not edit)
app = Flask(__name__)
last_epoch = 0
last_save_epoch = 0

def set_camera_mode(camera,cm):
        camera.change_framerate(cm["fr"])
        camera.shutter_speed(cm["speed"])
        camera.iso(cm["iso"])

def check_camera_mode(camera,current_state,future_state):
        global camera_mode
        if current_state != future_state:
                current_state = future_state
                camera_mode = camera_settings[current_state]
                set_camera_mode(camera,camera_mode)
        return current_state
                
def check_for_objects():
        global last_epoch
        global last_save_epoch
        global current_state
        global video_camera
        while True:
                #Add time checker in this thread
                future_state = lt.current_state()
                current_state = check_camera_mode(video_camera,current_state, future_state)
                try:
                        vis, found_obj = video_camera.get_object()
                        if found_obj==True:
                                if (time.time() - last_epoch) > email_update_interval:
                                        last_epoch = time.time()
                                        print "[INFO] sending email..."
                                        ret, jpeg = cv2.imencode('.jpg', vis)
                                        frame = jpeg.tobytes()
                                        sendEmail(frame)
                                        print "[INFO] done!"
                                if (time.time() - last_save_epoch) > save_update_interval:
                                        last_save_epoch = time.time()
                                        print "[INFO] saving hardcopy..."
                                        timestamp = lt.now()
                                        ts = timestamp.strftime("%Y-%m-%d-%H-%M-%S")
                                        filename = "/home/pi/Pictures/"+ts+".jpeg"
                                        cv2.imwrite(filename,vis)
                                        print "[INFO] done!"
                except:
                        print "Error sending email: ", sys.exc_info()[0]

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
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
