import asyncio

async def tcp_client():
    # 서버에 연결
    reader, writer = await asyncio.open_connection('10.20.0.162', 12345)

    print("Connected to the server. Type your message below (type 'exit' to quit):")
    
    while True:
        # 사용자 입력을 받음
        message = input("Enter message: ")

        # 'exit'를 입력하면 연결 종료
        if message.lower() == 'exit':
            print("Closing connection")
            break

        # 메시지를 서버로 전송
        writer.write(message.encode())
        await writer.drain()

        # 서버로부터의 응답을 기다림
        data = await reader.read(100)
        print(f"Received: {data.decode()}")

    # 연결 종료
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_client())
