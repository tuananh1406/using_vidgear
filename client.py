import pickle
import socket
import struct

import cv2

# create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host_ip = "192.168.2.195"  # paste your server ip address here
host_ip = "192.168.3.45"  # paste your server ip address here
port = 9999
client_socket.connect((host_ip, port))  # a tuple
data = b""
payload_size = struct.calcsize("Q")
while True:
    while len(data) < payload_size:
        if packet := client_socket.recv(4 * 1024):
            data += packet
        else:
            break
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4 * 1024)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    cv2.imshow("RECEIVING VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
client_socket.close()
