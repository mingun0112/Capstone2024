import cv2


cam = cv2.VideoCapture(0)

while cam.isOpened():
    status, frame = cam.read()

    if status:
        cv2.imshow("test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break