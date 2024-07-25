import os
import time

import cv2

# import numpy as np

filename = "video.avi"
frames_per_second = 24.0
out_fps = 30
res = "720p"
# used to record the time when we processed last frame
prev_frame_time = 0

# used to record the time at which we processed current frame
new_frame_time = 0


# Set resolution for the video capture
# Function adapted from https://kirr.co/0l6qmh
def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)


# Standard Video Dimensions Sizes
STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


# grab resolution dimensions and set video capture to it.
def get_dims(cap, res="1080p"):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    # change the current caputre device
    # to the resulting resolution
    change_res(cap, width, height)
    return width, height


# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    "avi": cv2.VideoWriter_fourcc(*"XVID"),
    # "mp4": cv2.VideoWriter_fourcc(*"H264"),
    "mp4": cv2.VideoWriter_fourcc(*"XVID"),
}


def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    return VIDEO_TYPE[ext] if ext in VIDEO_TYPE else VIDEO_TYPE["avi"]


cap = cv2.VideoCapture(0)
out = cv2.VideoWriter(filename, get_video_type(filename), out_fps, get_dims(cap, res))
# font which we will be using to display FPS
font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    ret, frame = cap.read()
    # time when we finish processing for this frame
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time

    # converting the fps into integer
    fps = int(fps)

    # converting the fps to string so that we can display it on frame
    # by using putText function
    fps = str(fps)

    # putting the FPS count on the frame
    cv2.putText(frame, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

    out.write(frame)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
out.release()
cv2.destroyAllWindows()
