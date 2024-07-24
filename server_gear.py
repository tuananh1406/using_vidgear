# import required libraries
import cv2

from vidgear.gears import NetGear

# Open suitable video stream, such as webcam on first index(i.e. 0)
stream = cv2.VideoCapture(0)

# define tweak flags
options = {"flag": 0, "copy": True, "track": False}

# Define Netgear Client at given IP address and define parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
server = NetGear(
    address="192.168.3.45",
    port="5454",
    protocol="tcp",
    pattern=0,
    logging=True,
    **options
)

# loop over until KeyBoard Interrupted
while True:
    try:
        # read frames from stream
        (grabbed, frame) = stream.read()

        # check for frame if not grabbed
        if not grabbed:
            break

        # {do something with the frame here}

        # send frame to server
        server.send(frame)

    except KeyboardInterrupt:
        break

# safely close video stream
stream.release()

# safely close server
server.close()
