import cv2

# 创建 VideoCapture 对象，参数 0 通常是默认摄像头，1 是 USB 摄像头
cap = cv2.VideoCapture(1)  # 根据需要调整摄像头索引

# 检查是否成功打开摄像头
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 获取摄像头名称（可能在某些系统上不支持）
camera_name = cap.get(cv2.CAP_PROP_FOURCC)
camera_name = "摄像头名称: " + str(camera_name)

# 获取分辨率
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
resolution = f"分辨率: {width}x{height}"

# 获取帧率
fps = cap.get(cv2.CAP_PROP_FPS)
fps_info = f"帧率: {fps} FPS"

# 打印摄像头信息
print(camera_name)
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
