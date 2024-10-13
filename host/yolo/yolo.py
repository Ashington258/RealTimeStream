import cv2
import requests
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8s.pt")


def detect_objects(frame):
    results = model(frame)
    detected_objects = []

    for result in results:
        for detection in result.boxes:
            label = result.names[int(detection.cls)]
            detected_objects.append(label)

    return detected_objects


def main():
    video_feed_url = "http://192.168.2.225:5000/video_feed"  # 主机视频流URL

    while True:
        response = requests.get(video_feed_url, stream=True)
        bytes_data = b""
        for chunk in response.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b"\xff\xd8")  # JPEG开始
            b = bytes_data.find(b"\xff\xd9")  # JPEG结束

            if a != -1 and b != -1:
                jpg = bytes_data[a : b + 2]  # 提取完整的JPEG图像
                bytes_data = bytes_data[b + 2 :]  # 移除处理过的部分
                nparr = np.frombuffer(jpg, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    detected_objects = detect_objects(frame)
                    print(f"Detected objects: {detected_objects}")
                    requests.post(
                        "http://192.168.2.225:5000/results",
                        json={"detected": detected_objects},
                    )


if __name__ == "__main__":
    main()
