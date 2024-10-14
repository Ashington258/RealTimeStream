import cv2

# 创建 VideoCapture 对象，CSI 摄像头通常使用索引 0 或 1
cap = cv2.VideoCapture(0)  # 根据需要调整摄像头索引

# 检查是否成功打开摄像头
if not cap.isOpened():
    print("无法打开 CSI 摄像头")
    exit()

# 无限循环读取摄像头帧并显示
while True:
    # 从摄像头捕获一帧图像
    ret, frame = cap.read()

    # 如果读取帧成功，则 ret 为 True
    if not ret:
        print("无法获取帧，请检查摄像头是否正常工作")
        break

    # 显示帧
    cv2.imshow("CSI Camera Video Stream", frame)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 释放摄像头资源
cap.release()

# 关闭所有 OpenCV 创建的窗口
cv2.destroyAllWindows()
