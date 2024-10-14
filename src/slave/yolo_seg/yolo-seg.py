import cv2
import numpy as np
import requests
import threading
import time
from ultralytics import YOLO
from queue import Queue

# 加载YOLO分割模型
model = YOLO("model/yolov8s-seg.pt")

# 视频流URL
url = "http://192.168.2.225:5000/video_feed"

# 队列用于线程间传递帧
frame_queue = Queue(maxsize=5)
result_queue = Queue(maxsize=5)


# 显示图像并进行YOLO分割的函数
def show_frame():
    while True:
        frame = result_queue.get()
        if frame is None:
            break

        cv2.imshow("Segmented Objects", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


# YOLO 分割检测函数
def detect_and_draw():
    while True:
        frame = frame_queue.get()
        if frame is None:
            result_queue.put(None)
            break

        start_time = time.time()  # 记录开始时间
        results = model(frame, verbose=False)[0]

        # 计算 FPS
        fps = 1 / (time.time() - start_time)

        # 遍历每个检测结果
        for mask, cls, conf in zip(
            results.masks.xy, results.boxes.cls, results.boxes.conf
        ):
            label = model.names[int(cls)]
            confidence = conf.item()

            # 创建掩码
            mask = mask.cpu().numpy().astype(np.uint8)
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            colored_mask = np.zeros_like(frame, dtype=np.uint8)
            colored_mask[:, :, 0] = mask * 255  # 蓝色通道
            colored_mask[:, :, 1] = mask * 0  # 绿色通道
            colored_mask[:, :, 2] = mask * 0  # 红色通道

            # 叠加掩码到原始帧
            frame = cv2.addWeighted(frame, 1, colored_mask, 0.5, 0)

            # 添加标签
            text = f"{label}: {confidence:.2f}"
            # 使用掩码的边界框作为标签位置
            x1, y1, x2, y2 = results.boxes.xyxy[int(cls)].cpu().numpy().astype(int)
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

        result_queue.put(frame)


def main():
    # 打开视频流
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print("无法连接到视频流")
        return

    # 启动显示线程
    threading.Thread(target=show_frame, daemon=True).start()

    # 启动检测线程
    threading.Thread(target=detect_and_draw, daemon=True).start()

    bytes_data = b""
    try:
        # 读取视频流
        for chunk in response.iter_content(chunk_size=4096):
            bytes_data += chunk
            a = bytes_data.find(b"\xff\xd8")  # JPEG 开始
            b = bytes_data.find(b"\xff\xd9")  # JPEG 结束
            if a != -1 and b != -1:
                jpg = bytes_data[a : b + 2]
                bytes_data = bytes_data[b + 2 :]
                frame = cv2.imdecode(
                    np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                )

                # 将帧放入队列，避免处理速度过快导致内存溢出
                if not frame_queue.full():
                    frame_queue.put(frame)
    except KeyboardInterrupt:
        print("中断程序")
    finally:
        # 结束线程
        frame_queue.put(None)
        result_queue.put(None)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
