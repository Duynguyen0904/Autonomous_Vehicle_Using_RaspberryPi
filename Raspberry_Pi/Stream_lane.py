import cv2
import socket
import pickle
import struct
import json
import serial

# import serial
ser = serial.Serial('PORT',115200, timeout=1) # Change 'PORT' to PORT_Raspberry_Pi connected to arduino instead

def send_to_arduino(serial_connection, data):
    serial_connection.write(data.encode("utf-8")) # should be converted to string

# Create socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 9000))  # Bind IP address of RaspberryPi and port 9000
server_socket.listen(1)
print('Server is running')

# Accept the connection from client (laptop)
client_socket, addr = server_socket.accept()

# Open camera and stream video
camera = cv2.VideoCapture(0)
while camera.isOpened():
    ret, frame = camera.read()
    frame = cv2.resize(frame, (480, 320))
    data = pickle.dumps(frame)
    client_socket.sendall(struct.pack("<L", len(data)) + data)
    
    data_receive = client_socket.recv(4096).decode()
    detected_texts = json.loads(data_receive)

    if detected_texts == "straight":
        send_to_arduino(ser, "f")
    elif detected_texts == "left":
        send_to_arduino(ser, "l")
    elif detected_texts == "right":
        send_to_arduino(ser, "r")
    print("Received:", detected_texts)

# Close connection
client_socket.close()
server_socket.close()
