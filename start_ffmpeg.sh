ffmpeg -f alsa -i default -acodec aac -strict -2 -ac 1 -f v4l2 -input_format mjpeg -framerate 30 -video_size 1920x1080 -i /dev/video0 -c:v libx264 -vf format=yuv420p -segment_time 10 -f segment -strftime 1 "raw/%d-%m-%Y_%H:%M:%S.mp4"
