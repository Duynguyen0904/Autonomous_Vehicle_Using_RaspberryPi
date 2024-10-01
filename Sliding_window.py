import cv2
from Algorithm import *
import time
import socket
import json
import pickle
import struct

def send_detected_texts(detected_texts):
    json_data = json.dumps(detected_texts)
    return json_data

## Create socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('id', 9000)) # Change 'id' to IP_Raspberry_Pi instead

data = b""
payload_size = struct.calcsize("<L")

# cap = cv2.VideoCapture(0)
start_time = time.time()

while True:
    while len(data) < payload_size:
        data += client_socket.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("<L", packed_msg_size)[0]
    
    while len(data) < msg_size:
        data += client_socket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)

    # _, frame = cap.read()
    t = [(132,351), (16,438), (629,418),(507,337)] ##real 
    frame = cv2.resize(frame, (640,480))
    ## undistorted frame
    undistorted = un_distort(frame)
    ## top view
    warp = lane_curve(frame, t)
    ## find white line and yellow line
    thresh = findEdge(warp)
    res = cv2.bitwise_and(warp, warp, mask=thresh)
    ## preprocess frame
    blur, edge = process(res)
    # draw the line
    rectangle, lane, left, right, y = line_fitting(edge)
    ## calculate the curve of the lane
    radius1 = radius(lane, left, right, y)
    #unWarp
    unWarp = UnWarp(lane, t)
    ## Draw ROI
    cv2.line(frame, t[0], t[1], (0,0,255), 2)
    cv2.line(frame, t[1], t[2], (0,0,255), 2)
    cv2.line(frame, t[2], t[3], (0,0,255), 2)
    cv2.line(frame, t[3], t[0], (0,0,255), 2)  

    ## Compared condition
    result, direct = Compare_condition(frame, unWarp, radius1)
    ## Display result
    cv2.imshow('IMG',result)

    data_send_to_pi = {"lane": direct}
    # print(data_send_to_pi)
    print(data_send_to_pi["lane"])

    json_data = send_detected_texts(direct)
    client_socket.sendall(json_data.encode())
    end_time = time.time()
    print("FPS:",1/(end_time-start_time))
    start_time = end_time
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cv2.destroyAllWindows()