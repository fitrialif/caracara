#!/usr/bin/python
"""
This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Original C implementation by:  ?
Python implementation by: Roman Stanchak, James Bowman
"""
import sys
import cv
from optparse import OptionParser
from functools import partial

# TODO:
# - Integrate with camshift.py
# - Put sprite on top of tracked object
# - Put bubble thoughts near faces


# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned 
# for accurate yet slow object detection. For a faster operation on real video 
# images the settings are: 
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING, 
# min_size=<minimum possible face size

min_size = (20, 20)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0
MAIN_WINDOW = "result"

def detect_faces(img, cascade):
    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / image_scale),
                   cv.Round (img.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    t = cv.GetTickCount()
    faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                 haar_scale, min_neighbors, haar_flags, min_size)
    t = cv.GetTickCount() - t
    print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.))
    for ((x, y, w, h), n) in faces:
        # the input to cv.HaarDetectObjects was resized, so scale the 
        # bounding box of each face and convert it to two CvPoints
        pt1 = (int(x * image_scale), int(y * image_scale))
        pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
        dark_violet = cv.RGB(148, 0, 211)
        cv.Rectangle(img, pt1, pt2, dark_violet, 1, 8, 0)

    return img
    
    
def capture_from_webcam(index, func):
    capture = cv.CreateCameraCapture(index)
    frame_copy = None
    while True:
        frame = cv.QueryFrame(capture)
        if not frame:
            cv.WaitKey(0)
            break
        if not frame_copy:
            frame_copy = cv.CreateImage((frame.width, frame.height),
                                        cv.IPL_DEPTH_8U, frame.nChannels)
        if frame.origin == cv.IPL_ORIGIN_TL:
            cv.Copy(frame, frame_copy)
        else:
            cv.Flip(frame, frame_copy, 0)
        
        img = func(frame_copy)
        cv.ShowImage(MAIN_WINDOW, img)

        if cv.WaitKey(10) >= 0:
            break


def main():
    parser = OptionParser(usage = "usage: %prog [options] [camera_index]")
    parser.add_option("-c", "--cascade", action="store", dest="cascade", type="str",
                      help="Haar cascade file, default %default",
                      default="cascades/haarcascade_frontalface_alt.xml")
    parser.add_option("-f", "--file", action="store", dest="file", type="str",
                      help="Image file")
    (options, args) = parser.parse_args()
    
    cascade = cv.Load(options.cascade)

    cv.NamedWindow(MAIN_WINDOW, cv.CV_WINDOW_AUTOSIZE)
    
    if options.file:
        img = cv.LoadImage(options.file, 1)
        img = detect_faces(img, cascade)
        cv.ShowImage(MAIN_WINDOW, img)
        cv.WaitKey(0)
    else:
        index = args[:1] and args[0].isdigit() and int(args[0]) or 0
        capture_from_webcam(index, partial(detect_faces, cascade=cascade))

    cv.DestroyWindow(MAIN_WINDOW)


if __name__ == '__main__':
    main()