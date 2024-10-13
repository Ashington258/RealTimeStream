from flask import Flask, Response
import cv2
import threading

app = Flask(__name__)

# 打开摄像头，设置分辨率和帧率
camera = cv2.VideoCapture(1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
camera.set(cv2.CAP_PROP_FPS, 15)

# 全局变量和线程锁
frame = None
lock = threading.Lock()


# 后台帧捕获线程
def capture_frames():
    global frame
    while True:
        success, new_frame = camera.read()
        if success:
            with lock:
                frame = new_frame


threading.Thread(target=capture_frames, daemon=True).start()


# 生成视频流帧
def generate_frames():
    global frame
    while True:
        with lock:
            if frame is None:
                continue
            # 编码为JPEG并设置较低的质量以减少延迟
            ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            frame_data = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_data + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    # 启用多线程，并设置 host 为 0.0.0.0
    app.run(host="192.168.2.225", port=5000, threaded=True)
