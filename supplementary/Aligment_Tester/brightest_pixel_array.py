import cv
import cv2
import numpy as np
import sys

"""
Creates an array of values using the brightest pixle in each frame
"""

print "loading " + sys.argv[1]

cap = cv2.VideoCapture(sys.argv[1])
ledArr = np.zeros(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))

print "Finding brightest pixle value per frame"
while True:

    ret, frame = cap.read()
    
    FC = cap.get(cv.CV_CAP_PROP_POS_FRAMES)
    print FC
    if ret:
        grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        ledArr[FC-1] = np.amax(red)
    else:
        break

np.save(sys.argv[1] + ".npy", ledArr)
print "Saved " + sys.argv[1] + ".npy"
