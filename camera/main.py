import serial
import json
import cv2

#시리얼포트 객체 ser을 생성
#pc와 스위치 시리얼포트 접속정보
ser = serial.Serial(
    port = 'COM7', 
    baudrate=115200, 
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=8
    )

#시리얼포트 접속
ser.isOpen()
while True:
    data = ser.readline()

    if data:
        json_str = data.decode('utf-8').strip()
        
        data = json.loads(json_str)
        print(data["A"])
#시리얼포트 번호 출력
