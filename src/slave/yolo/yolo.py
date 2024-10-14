import cv2
import numpy as np
import requests
import threading
import time
from ultralytics import YOLO

# 加载YOLO模型
model = YOLO("model/yolov8s.pt")

# 全局变量用于存储当前视频帧
frame = None

# 视频流URL
url = "http://192.168.2.225:5000/video_feed"


# 显示图像并进行YOLO检测的函数
def show_frame():
    global frame
    while True:
        if frame is not None:
            start_time = time.time()  # 记录开始时间
            # 目标检测
            detected_objects = detect_objects(frame)

            # 计算 FPS
            fps = 1 / (time.time() - start_time)

            # 在帧上绘制检测结果和FPS
            draw_detections(frame, detected_objects, fps)

            # 显示图像
            cv2.imshow("Detected Objects", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cv2.destroyAllWindows()


# YOLO 目标检测函数
def detect_objects(frame):
    results = model(frame)
    detected_objects = []

    for result in results:
        for detection in result.boxes:
            label = result.names[int(detection.cls)]
            confidence = detection.conf
            detected_objects.append((label, confidence, detection.xyxy))
    return detected_objects


# 在图像上绘制检测结果的函数
def draw_detections(frame, detections, fps):
    for label, confidence, box in detections:
        box = box.cpu().numpy() if hasattr(box, "cpu") else box.numpy()
        box = box.squeeze()
        x1, y1, x2, y2 = map(int, box[:4])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        confidence = confidence.item()
        text = f"{label}: {confidence:.2f}"
        cv2.putText(
            frame,
            text,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )

    # 绘制FPS
    cv2.putText(
        frame,
        f"FPS: {fps:.2f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )


def main():
    global frame
    # 打开视频流
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print("无法连接到视频流")
        exit()

    # 启动显示线程
    threading.Thread(target=show_frame, daemon=True).start()

    bytes_data = b""
    # 读取视频流
    for chunk in response.iter_content(chunk_size=4096):
        bytes_data += chunk
        a = bytes_data.find(b"\xff\xd8")  # JPEG 开始
        b = bytes_data.find(b"\xff\xd9")  # JPEG 结束
        if a != -1 and b != -1:
            jpg = bytes_data[a : b + 2]
            bytes_data = bytes_data[b + 2 :]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
