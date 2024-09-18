import asyncio
import websockets
import cv2
import numpy as np
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
async def handle_connection(websocket, path):
    cap = cv2.VideoCapture(0)  # 카메라 열기

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 이미지 인코딩
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        data = buffer.tobytes()

        # WebSocket을 통해 이미지 전송
        await websocket.send(data)
        await asyncio.sleep(0)  # 프레임 속도 조절

    cap.release()

start_server = websockets.serve(handle_connection, "localhost", 10001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
