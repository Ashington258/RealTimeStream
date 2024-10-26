import cv2
import subprocess

# 创建 VideoCapture 对象，参数 0 通常是默认摄像头，1 是 USB 摄像头
cap = cv2.VideoCapture(0)  # 根据需要调整摄像头索引

# 检查是否成功打开摄像头
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 获取摄像头的设备路径
device_index = 1  # 根据需要调整
device_path = f"/dev/video{device_index}"

# 使用 v4l2-ctl 获取摄像头名称和其他信息
try:
    output = subprocess.check_output(
        ["v4l2-ctl", "--device=" + device_path, "--all"], universal_newlines=True
    )
    print("摄像头信息:")
    print(output)
except subprocess.CalledProcessError as e:
    print(f"获取摄像头信息失败: {e}")

# 获取分辨率
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
resolution = f"分辨率: {width}x{height}"

# 获取帧率
fps = cap.get(cv2.CAP_PROP_FPS)
fps_info = f"帧率: {fps} FPS"

# 打印摄像头分辨率和帧率
print(resolution)
print(fps_info)

# 无限循环读取摄像头帧并显示
while True:
    # 从摄像头捕获一帧图像
    ret, frame = cap.read()

    # 如果读取帧成功，则 ret 为 True
    if not ret:
        print("无法获取帧，请检查摄像头是否正常工作")
        break

    # 显示帧
    cv2.imshow("USB Camera Video Stream", frame)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 释放摄像头资源
cap.release()

# 关闭所有 OpenCV 创建的窗口
cv2.destroyAllWindows()
