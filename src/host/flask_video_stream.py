from flask import Flask, Response
import cv2
import threading
import json
from servos.servos import ServosInit, set_servo_pwm, cleanup  # 导入舵机控制模块


class VideoStream:
    def __init__(self, camera_index=1, width=480, height=640, fps=15):
        self.camera = cv2.VideoCapture(camera_index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.camera.set(cv2.CAP_PROP_FPS, fps)
        self.frame = None
        self.lock = threading.Lock()
        self.start_frame_capture()

    def start_frame_capture(self):
        threading.Thread(target=self.capture_frames, daemon=True).start()

    def capture_frames(self):
        while True:
            success, new_frame = self.camera.read()
            if success:
                with self.lock:
                    self.frame = new_frame

    def generate_frames(self):
        while True:
            with self.lock:
                if self.frame is None:
                    continue
                ret, buffer = cv2.imencode(
                    ".jpg", self.frame, [cv2.IMWRITE_JPEG_QUALITY, 30]
                )
                frame_data = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_data + b"\r\n"
            )


def create_app(camera_config, pwm):
    app = Flask(__name__)
    video_stream = VideoStream(
        camera_index=camera_config["index"],
        width=camera_config["width"],
        height=camera_config["height"],
        fps=camera_config["fps"],
    )

    @app.route("/video_feed")
    def video_feed():
        return Response(
            video_stream.generate_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    # 其他路由可以加入舵机控制逻辑
    @app.route("/servo_control/<int:pulse_width>")
    def servo_control(pulse_width):
        # 设置舵机脉宽
        set_servo_pwm(pwm, 50, pulse_width)
        return {"status": "success", "pulse_width": pulse_width}

    return app


def load_config(file_path="src/config.json"):
    with open(file_path) as config_file:
        return json.load(config_file)


if __name__ == "__main__":
    config = load_config()

    # 初始化舵机
    output_pin = 32  # PWM 输出的 GPIO 管脚
    pwm = ServosInit(output_pin, frequency=50, initial_pulse_width_us=1500)

    try:
        # 启动 Flask 应用
        app = create_app(config["camera"], pwm)
        app.run(host=config["host"], port=config["port"], threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        # 清理舵机和 GPIO 资源
        cleanup(pwm)
