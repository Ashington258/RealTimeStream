import cv2
import numpy as np
import requests
import threading

# 视频流URL
url = "http://192.168.2.225:5000/video_feed"

# 打开视频流
response = requests.get(url, stream=True)
if response.status_code != 200:
    print("无法连接到视频流")
    exit()

bytes_data = b""
frame = None


# 显示图像的函数
def show_frame():
    global frame
    while True:
        if frame is not None:
            cv2.imshow("Received Video Stream", frame)
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break
    cv2.destroyAllWindows()


# 启动显示线程
threading.Thread(target=show_frame, daemon=True).start()

# 读取视频流
for chunk in response.iter_content(chunk_size=4096):
    bytes_data += chunk
    a = bytes_data.find(b"\xff\xd8")
    b = bytes_data.find(b"\xff\xd9")
    if a != -1 and b != -1:
        jpg = bytes_data[a : b + 2]
        bytes_data = bytes_data[b + 2 :]
        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

# 释放资源
cv2.destroyAllWindows()
