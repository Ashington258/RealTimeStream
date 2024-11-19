import cv2

camera = cv2.VideoCapture(0)  # 替换索引为实际的摄像头索引

if not camera.isOpened():
    print("Failed to open camera.")
else:
    print("Camera opened successfully.")
    ret, frame = camera.read()
    if ret:
        print("Frame captured successfully.")
    else:
        print("Failed to capture frame.")

camera.release()
