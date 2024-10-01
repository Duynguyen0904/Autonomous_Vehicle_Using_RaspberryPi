import torch
import cv2
import time
import os
import numpy as np
from datetime import datetime
import socket
import pickle
import json
import struct

start_time = time.time()
def send_detected_texts(detected_texts):
    json_data = json.dumps(detected_texts)
    return json_data

def crop_write(crop):
    # elif crop != None:
    current_time = datetime.now()
    time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    path = "./file/crop_img"
    filename = f"cropped_{time_str}.jpg"
    fullpath = os.path.join(path, filename)
    cv2.imwrite(fullpath, crop)

def color_classify(frame):
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

    lower_red = np.array([2, 100, 100])
    upper_red = np.array([18, 255, 255])

    lower_yellow = np.array([21, 100, 100])
    upper_yellow = np.array([30, 255, 255])

    lower_green = np.array([60, 100, 100])
    upper_green = np.array([90, 255, 255])

    red_mask = cv2.inRange(hsv_image, lower_red, upper_red)
    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

    red_pixels = cv2.countNonZero(red_mask)
    yellow_pixels = cv2.countNonZero(yellow_mask)
    green_pixels = cv2.countNonZero(green_mask)

    # print(red_pixels)
    # print(yellow_pixels)

    if (red_pixels > yellow_pixels and red_pixels > green_pixels):
        color = "red"
    elif (yellow_pixels > red_pixels and yellow_pixels > green_pixels):
        color = "yellow"
    elif (green_pixels > red_pixels and green_pixels > yellow_pixels):
        color = "green"
    else:
        color = "Unknown"
    return color

def detectx (frame, model):
    frame = [frame]
    print(f"[INFO] Detecting. . . ")
    results = model(frame)

    labels, coordinates = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
    return labels, coordinates

def plot_boxes(results, frame):
    labels, cord = results
    n = len(labels)
    x_shape, y_shape = frame.shape[1], frame.shape[0]
    detected_box = []

    print(f"[INFO] Total {n} detections. . . ")
    ### looping through the detections
    for i in range(n):
        row = cord[i]
        if row[4] >= 0.8: ### threshold value for detection. We are discarding everything below this value
            print(f"[INFO] Extracting BBox coordinates. . . ")
            x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
            obj = frame[int(y1):int(y2), int(x1):int(x2)]
            crop_write(obj)
            text_d = color_classify(obj)
            detected_box.append(text_d)
            accuracy = round(float(row[4]),2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) ## BBox
            cv2.rectangle(frame, (x1, y1-20), (x2, y1), (0, 255,0), -1) ## for text label background
            cv2.putText(frame, f"{text_d}_{accuracy}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255), 2)
    return frame, detected_box

model =  torch.hub.load('./yolov5-master', 'custom', source ='local', path='./best_light.pt',force_reload=True) ### The repo is stored locally

# classes = ['red','yellow','green']#model.names ### class names in string format
# classes = ['no_overtaking','turn_left','stop'] 

# Create socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('id', 9000)) # Change 'id' to IP_Raspberry_Pi instead

data = b""
payload_size = struct.calcsize("<L")
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
    # frame = cv2.imread(f'./file/img/{i}.jpg')
    frame = cv2.resize(frame, (640, 480))
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = detectx(frame, model = model)
    frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
    frame, text_send = plot_boxes(results, frame)

    # Send data to Raspberry
    json_data = send_detected_texts(text_send)
    client_socket.sendall(json_data.encode())

    end_time = time.time()
    print('FPS:',1/(end_time-start_time))
    start_time = end_time
    cv2.imshow("img_only", frame)
    if cv2.waitKey(50) & 0xff == ord('q'):
        break    
    
cv2.destroyAllWindows()