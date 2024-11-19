import cv2
import threading
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import atexit


class VideoStream:
    def __init__(self, camera_index=0, width=640, height=480, fps=30, fourcc="MJPG"):
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            raise ValueError(f"Camera with index {camera_index} could not be opened.")

        # 设置摄像头参数
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.camera.set(cv2.CAP_PROP_FPS, fps)
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))

        print(
            f"Camera initialized with resolution {width}x{height} at {fps} FPS using {fourcc}."
        )

        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.start_frame_capture()

    def start_frame_capture(self):
        threading.Thread(target=self.capture_frames, daemon=True).start()

    def capture_frames(self):
        while self.running:
            success, frame = self.camera.read()
            if success:
                with self.lock:
                    self.frame = frame

    def get_encoded_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            # 将帧编码为 JPEG 格式
            ret, buffer = cv2.imencode(
                ".jpg", self.frame, [cv2.IMWRITE_JPEG_QUALITY, 70]
            )
            return base64.b64encode(buffer).decode("utf-8")

    def stop(self):
        self.running = False
        self.camera.release()
        print("Camera released!")


def create_app(camera_config):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key"
    socketio = SocketIO(app, cors_allowed_origins="*")

    video_stream = VideoStream(
        camera_index=camera_config["index"],
        width=camera_config["width"],
        height=camera_config["height"],
        fps=camera_config["fps"],
        fourcc=camera_config.get("fourcc", "MJPG"),
    )

    # 确保摄像头资源在程序退出时被释放
    atexit.register(video_stream.stop)

    @socketio.on("start_stream")
    def handle_start_stream():
        def stream_video():
            while video_stream.running:
                frame = video_stream.get_encoded_frame()
                if frame:
                    emit("video_frame", {"frame": frame}, broadcast=True)

        threading.Thread(target=stream_video, daemon=True).start()

    @socketio.on("stop_stream")
    def handle_stop_stream():
        video_stream.stop()

    @app.route("/")
    def index():
        return render_template("index.html")  # 前端页面用于显示视频流

    return app, socketio


def load_config(file_path="RealTimeStream/src/config.json"):
    with open(file_path) as config_file:
        return json.load(config_file)


if __name__ == "__main__":
    config = load_config()

    try:
        app, socketio = create_app(config["camera"])
        socketio.run(app, host=config["host"], port=config["port"], debug=True)
    except KeyboardInterrupt:
        pass
