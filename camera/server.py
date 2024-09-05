import socket
import cv2
import numpy as np
import threading

# socket에서 수신한 버퍼를 반환하는 함수
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: 
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def handle_client(port):
    HOST = ''
    
    # TCP 소켓 생성
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port))
    s.listen(10)
    print(f'Socket now listening on port {port}')

    conn, addr = s.accept()
    print(f'Connected by {addr} on port {port}')

    while True:
        # client에서 받은 stringData의 크기 수신
        length = recvall(conn, 16)
        if length is None:
            break
        stringData = recvall(conn, int(length))
        if stringData is None:
            break
        data = np.frombuffer(stringData, dtype='uint8')

        # data를 디코딩하여 이미지를 복원
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        
        # 이미지 표시
        cv2.imshow(f'ImageWindow - Port {port}', frame)
        cv2.waitKey(1)

    conn.close()

# 각각 다른 포트에서 수신하도록 스레드 생성
ports = [8485, 8486]
threads = []

for port in ports:
    t = threading.Thread(target=handle_client, args=(port,))
    t.start()
    threads.append(t)

# 모든 스레드가 종료될 때까지 대기
for t in threads:
    t.join()

cv2.destroyAllWindows()
