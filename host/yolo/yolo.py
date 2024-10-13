import cv2
import requests
import numpy as np
from ultralytics import YOLO
import time

# 加载YOLO模型
model = YOLO("yolov8s.pt")


def detect_objects(frame):
    # 对图像进行YOLO检测
    results = model(frame)
    detected_objects = []

    # 处理检测结果
    for result in results:
        for detection in result.boxes:
            label = result.names[int(detection.cls)]
            confidence = detection.conf  # 置信度
            detected_objects.append(
                (label, confidence, detection.xyxy)
            )  # 包含标签、置信度和边界框

    return detected_objects


def draw_detections(frame, detections, fps):
    # 在图像上绘制检测到的对象
    for label, confidence, box in detections:
        # 将张量转换为 NumPy 数组并去除多余维度
        box = box.cpu().numpy() if hasattr(box, "cpu") else box.numpy()
        box = box.squeeze()  # 去掉多余的维度，确保是4个值的数组
        x1, y1, x2, y2 = map(int, box[:4])  # 转换为整数并只取前4个值
        # 绘制边界框
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        # 将置信度从张量转换为Python浮点数
        confidence = confidence.item()
        # 添加标签和置信度
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

    # 在图像上绘制FPS
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
                    start_time = time.time()  # 记录处理开始时间
                    # 检测对象
                    detected_objects = detect_objects(frame)
                    # 在图像上绘制检测结果
                    draw_detections(frame, detected_objects, 0)  # 初始FPS为0
                    # 显示检测后的图像
                    cv2.imshow("Detected Objects", frame)

                    # 发送检测结果到主机
                    requests.post(
                        "http://192.168.2.225:5000/results",
                        json={
                            "detected": [obj[0] for obj in detected_objects]
                        },  # 只发送标签
                    )

                    end_time = time.time()  # 记录处理结束时间
                    fps = 1 / (end_time - start_time)  # 计算FPS
                    draw_detections(frame, detected_objects, fps)  # 重新绘制FPS

                # 按 'q' 键退出
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
