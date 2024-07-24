# import required libraries
from datetime import datetime

import cv2
from vidgear.gears import CamGear, WriteGear

# open any valid video stream(for e.g `myvideo.avi` file)
stream = CamGear(source=0).start()

# Define writer with default parameters and suitable output filename for e.g. `Output.mp4`
writer = WriteGear(output="Output.mp4", logging=True)
now = datetime.now()
print("Start time: ", now)

# loop over
while True:
    # read frames from stream
    frame = stream.read()

    # check for frame if Nonetype
    if frame is None:
        break

    # {do something with the frame here}

    # write frame to writer
    writer.write(frame)
    if (datetime.now() - now).seconds > 5:
        print("5 seconds passed")
        break

    # Show output window
    # cv2.imshow("Output Frame", frame)

    # check for 'q' key if pressed
    # key = cv2.waitKey(1) & 0xFF
    # if key == ord("q"):
    #     break

# close output window
cv2.destroyAllWindows()

# safely close video stream
stream.stop()

# safely close writer
writer.close()
