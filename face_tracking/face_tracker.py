# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import pantilthat

width = 640
height = 480
# tolerance of face centering relative to frame dimensions
w_tol = 0.05
h_tol = 0.05


tilt = -20
pan = 0
tilt_velocity = 1
pan_velocity = 1
pan_limits = [-90,90]
tilt_limits = [-90,90]



# create cascade classifier that will look for a face
faceCascade = cv2.CascadeClassifier("../open_cv_tutorial/Resources/haarcascades/haarcascade_frontalface_default.xml")

# initialize pantilt servos
# tilt is servo one
# pan is servo two
pantilthat.servo_one(tilt)
pantilthat.servo_two(pan)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# 180 to flip camera
camera.rotation = 180
camera.resolution = (width, height)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

def find_faces(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(imgGray, 1.1, 4)
    return faces

def draw_face_rect(img, faces):
    for (x, y, w, h) in faces:
        cv2.putText(img, "Face", (x, y), cv2.FONT_HERSHEY_COMPLEX,
                    1, (0, 255, 0), 2)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return img, faces

def check_limit(angle, angle_limits):
    limit = 0
    if angle > angle_limits[1] or angle < angle_limits[0]:
        if angle > angle_limits[1]:
            angle = angle_limits[1]
            limit = 1
        elif angle < angle_limits[0]:
            angle = angle_limits[0]
            limit = -1
    return angle, limit

def pan_camera(pantilthat, pan_velocity, tilt_velocity, pan_limits, tilt_limits):
    pan = pantilthat.get_servo_two() + pan_velocity
    tilt = pantilthat.get_servo_one()
    pan, pan_success = check_limit(pan, pan_limits)
    if pan_success != 0:
        pan_velocity = -pan_velocity
        tilt = tilt + tilt_velocity
        tilt, tilt_success = check_limit(tilt, tilt_limits)
        if tilt_success != 0:
            tilt_velocity = -tilt_velocity

    pantilthat.servo_one(tilt)
    pantilthat.servo_two(pan)
    time.sleep(0.0005)
    return pantilthat, pan_velocity, tilt_velocity
        
def center_face(face, dimension, tol, pantilthat, pan_velocity, tilt_velocity, pan_limits, tilt_limits):
    pan = pantilthat.get_servo_two()
    tilt = pantilthat.get_servo_one()
    x = face[0] + face[2]/2.0
    y = face[1] + face[3]/2.0
    if abs(x-dimension[0]/2.0) > dimension[0] * tol[0]:
        if x < dimension[0]/2.0:
            pan = pan + abs(pan_velocity)
        else:
            pan = pan - abs(pan_velocity)
    
    if abs(y-dimension[1]/2.0) > dimension[1] * tol[1]:    
        if y > dimension[1]/2.0:
            tilt = tilt + abs(tilt_velocity)
        else:
            tilt = tilt - abs(tilt_velocity)
    
    pan, _ = check_limit(pan, pan_limits)
    tilt, _ = check_limit(tilt, tilt_limits)
    
    pantilthat.servo_one(tilt)
    pantilthat.servo_two(pan)
    time.sleep(0.0005)


# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    img = frame.array
    
    faces = find_faces(img)
    
    draw_face_rect(img, faces)
    
    # if no faces are found, pan the camera around
    if len(faces) == 0:
        _, pan_velocity, tilt_velocity = pan_camera(pantilthat, pan_velocity, tilt_velocity, pan_limits, tilt_limits)
    # track the face by trying to keep it centered in the frame. only tracks the first face in the list
    else:
        center_face(faces[0], [width, height], [w_tol, h_tol], pantilthat, pan_velocity, tilt_velocity, pan_limits, tilt_limits)
    # show the frame
    cv2.imshow("Frame", img)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
