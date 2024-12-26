import pickle
import socket
import struct

import cv2

# create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host_ip = "192.168.2.195"  # paste your server ip address here
host_ip = "192.168.3.91"  # paste your server ip address here
port = 9999
client_socket.connect((host_ip, port))  # a tuple

vid = None

# Socket Accept
while True:
    try:
        client_socket, addr = server_socket.accept()
        print("GOT CONNECTION FROM:", addr)
        if client_socket:
            print("open camera")
            vid = cv2.VideoCapture(0)

            while vid.isOpened():
                img, frame = vid.read()
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
    except Exception as e:
        print(e)
        if client_socket:
            client_socket.close()
        if vid:
            vid.release()
        continue
