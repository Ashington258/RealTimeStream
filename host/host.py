import cv2
import socket
import struct
import numpy as np

# 设置 UDP 套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("0.0.0.0", 5005))  # 绑定到所有可用接口

# 最大的数据报大小
MAX_DGRAM = 65507
frame_data = b""

while True:
    # 先接收图像的大小信息
    packed_size, _ = client_socket.recvfrom(struct.calcsize("L"))
    frame_size = struct.unpack("L", packed_size)[0]

    # 接收分片数据，直到接收到完整的帧
    while len(frame_data) < frame_size:
        data, _ = client_socket.recvfrom(MAX_DGRAM)  # 缓冲区大小设置为 MAX_DGRAM
        frame_data += data

    # 当完整的帧数据接收完毕后，进行解码
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # 清空缓冲区以接收下一帧
    frame_data = b""

    if frame is not None:
        # 处理图像（这里可以进行图像处理）
        processed_frame = cv2.Canny(frame, 100, 200)  # 示例：边缘检测

        # 显示图像（可选）
        cv2.imshow("Processed Frame", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

client_socket.close()
cv2.destroyAllWindows()
