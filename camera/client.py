# -*- coding: utf8 -*-
import cv2
import socket
import numpy as np
 
## TCP 사용
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
## server ip, port
s.connect(('localhost', 8485))
 
## webcam 이미지 capture
cam = cv2.VideoCapture(0)

 
## 0~100에서 90의 이미지 품질로 설정 (default = 95)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
 
while True:

    ret, frame = cam.read()

    result, frame = cv2.imencode('.jpg', frame, encode_param)

    data = np.array(frame)
    stringData = data.tostring()
    s.sendall((str(len(stringData))).encode().ljust(16) + stringData)
 
cam.release()