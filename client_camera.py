import asyncio
import websockets
import cv2
import numpy as np



async def receive_images():
    uri = "ws://localhost:10001"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                cv2.imshow("Received Image", img)
                cv2.waitKey(1)

if __name__ == "__main__":
    asyncio.run(receive_images())
