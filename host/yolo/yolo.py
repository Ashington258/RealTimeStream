import cv2
import requests
import numpy as np
from ultralytics import YOLO

# 加载YOLOv8s模型
model = YOLO("yolov8s.pt")


def detect_objects(frame):
    results = model(frame)
    detected_objects = []

    for result in results:
        for detection in result.boxes:
            label = result.names[int(detection.cls)]
            detected_objects.append(label)
            # 你可以在这里绘制矩形框和标签

    return detected_objects


def main():
    video_feed_url = "http://192.168.2.225:5000/video_feed"  # 主机视频流URL

    while True:
        response = requests.get(video_feed_url, stream=True)
        for chunk in response.iter_content(chunk_size=1024):
            # 按帧处理
            if b"\r\n" in chunk:
                frame_data = chunk.split(b"\r\n\r\n")[1].split(b"\r\n")[0]
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    detected_objects = detect_objects(frame)
                    print(f"Detected objects: {detected_objects}")

                    # 返回检测结果给主机
                    requests.post(
                        "http://192.168.2.225:5000/results",
                        json={"detected": detected_objects},
                    )


if __name__ == "__main__":
    main()


