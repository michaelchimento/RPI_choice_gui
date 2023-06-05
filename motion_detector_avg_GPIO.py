'''
Author: Michael Chimento
This code uses a modified version of Gaussian Mixture Model background
subtraction method object detection written by Addison Sears-Collins
'''
# import the necessary packages
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time # Provides time-related functions
import cv2 # OpenCV library
import numpy as np # Import NumPy library

#setup gpio
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
output_pin = 12 #GPIO15, 6th pin from top right
GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.output(output_pin, GPIO.LOW)
 
# Initialize the camera
camera = PiCamera()
 
# Set the camera resolution
camera.resolution = (640, 480)
 
# Set the number of frames per second
camera.framerate = 30

video_length = 180
 
# Generates a 3D RGB array and stores it in rawCapture
raw_capture = PiRGBArray(camera, size=(640, 480))
 
# Create the background subtractor object
# Feel free to modify the history as you see fit.
back_sub = cv2.createBackgroundSubtractorMOG2(history=150,
  varThreshold=25, detectShadows=True)
 
# Wait a certain number of seconds to allow the camera time to warmup
time.sleep(0.1)
 
# Create kernel for morphological operation. You can tweak
# the dimensions of the kernel.
# e.g. instead of 20, 20, you can try 30, 30
kernel = np.ones((20,20),np.uint8)

min_area = 100
accWeighted_alpha=0.6
thresh_val = 255
dilate_iter = 4


avg = None
flag = False
vid_num=0
print("sleeping for 5 sec")
time.sleep(5)
lastCapture=time.time()
# Capture frames continuously from the camera
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
     
    # Grab the raw NumPy array representing the image
    image = frame.array
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0)
 
    # if the average frame is None, initialize it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        raw_capture.truncate(0)
        continue# Convert to foreground mask
    
    cv2.accumulateWeighted(gray, avg, accWeighted_alpha)
    
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
       
    # If a pixel is less than ##, it is considered black (background). 
    # Otherwise, it is white (foreground). 255 is upper limit.
    # Modify the number after fg_mask as you see fit.
    _, thresh = cv2.threshold(frame_delta, 20, thresh_val, cv2.THRESH_BINARY)

    thresh = cv2.dilate(thresh, None, iterations=dilate_iter)
     # Find the contours of the object inside the binary image
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    areas = [cv2.contourArea(c) for c in contours]
    num_obj = len(areas)
    
    current_time=time.time()
    
    if num_obj<1:
        if not flag:
            #print("no objects")
            pass
         
    else:
        if max(areas)<min_area:
            print("small object detected {}".format(max(areas)))
            
        else:
            if vid_num==0 or (not flag and (current_time - lastCapture > (video_length + 4))):
                print("large object detected {}".format(max(areas)))
                print("Changing board pin {} to high for {}s".format(output_pin, video_length))
                GPIO.output(output_pin, GPIO.HIGH)
                flag=True
                vid_num += 1
                print("video number {}".format(vid_num))
                lastCapture=time.time()
                # Find the largest moving object in the image
                max_index = np.argmax(areas)
                cnt = contours[max_index]
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(thresh, (x, y), (x + w, y + h), (0, 255, 255), 2)
                
    if flag:   
        if current_time - lastCapture > video_length:
            print("Changing board pin {} back to low...".format(output_pin))
            GPIO.output(output_pin, GPIO.LOW)
            flag=False

    cv2.imshow('Frame',image)
    
    # Wait for keyPress for 1 millisecond
    key = cv2.waitKey(5) & 0xFF
  
    # Clear the stream in preparation for the next frame
    raw_capture.truncate(0)
     
    # If "q" is pressed on the keyboard, 
    # exit this loop
    if key == ord("q"):
      break
 
# Close down windows
cv2.destroyAllWindows()
GPIO.cleanup()
print("Cleaned up")
