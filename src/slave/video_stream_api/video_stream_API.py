import cv2
import numpy as np
import requests
import threading


class VideoStream:
    def __init__(self, url):
        self.url = url
        self.bytes_data = b""
        self.frame = None
        self.running = True

        # 启动读取线程
        self.thread = threading.Thread(target=self.read_stream, daemon=True)
        self.thread.start()

    def read_stream(self):
        response = requests.get(self.url, stream=True)
        if response.status_code != 200:
            print("无法连接到视频流")
            self.running = False
            return

        for chunk in response.iter_content(chunk_size=4096):
            self.bytes_data += chunk
            a = self.bytes_data.find(b"\xff\xd8")
            b = self.bytes_data.find(b"\xff\xd9")
            if a != -1 and b != -1:
                jpg = self.bytes_data[a : b + 2]
                self.bytes_data = self.bytes_data[b + 2 :]
                self.frame = cv2.imdecode(
                    np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                )

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running


def main():
    # 视频流URL
    url = "http://192.168.2.225:5000/video_feed"
    video_stream = VideoStream(url)

    # 显示图像的函数
    while video_stream.is_running():
        frame = video_stream.get_frame()
        if frame is not None:
            cv2.imshow("Received Video Stream", frame)
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break

    video_stream.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
