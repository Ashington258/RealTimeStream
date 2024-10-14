import subprocess


def list_usb_devices():
    print("USB Devices:")
    # 使用 lsusb 命令列出 USB 设备
    try:
        result = subprocess.run(["lsusb"], stdout=subprocess.PIPE, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"无法列出 USB 设备: {e}")


def list_camera_devices():
    print("Camera Devices:")
    # 使用 v4l2-ctl 命令列出摄像头设备
    try:
        result = subprocess.run(
            ["v4l2-ctl", "--list-devices"], stdout=subprocess.PIPE, text=True
        )
        print(result.stdout)

        # 获取每个摄像头的详细信息
        device_lines = result.stdout.strip().split("\n")
        for line in device_lines:
            if "video" in line:
                device_path = line.split()[-1]  # 获取设备路径
                print(f"\n详细信息 for {device_path}:")
                try:
                    detail_result = subprocess.run(
                        ["v4l2-ctl", "--device=" + device_path, "--all"],
                        stdout=subprocess.PIPE,
                        text=True,
                    )
                    print(detail_result.stdout)
                except Exception as e:
                    print(f"无法获取设备 {device_path} 的详细信息: {e}")
    except Exception as e:
        print(f"无法列出摄像头设备: {e}")


if __name__ == "__main__":
    list_usb_devices()
    list_camera_devices()


