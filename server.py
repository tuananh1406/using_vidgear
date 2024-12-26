import socket
import cv2
import pickle
import struct

# Socket Create
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print("HOST IP:", host_ip)
port = 9999
socket_address = (host_ip, port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:", socket_address)
client_socket = None
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
