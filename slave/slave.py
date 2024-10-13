import cv2
import socket
import struct

# Setup video capture
cap = cv2.VideoCapture(1)  # Change to your camera source
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

# Set up UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.2.117", 5005)  # Windows host address and port

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode the frame as JPEG to reduce data size
    ret, buffer = cv2.imencode(".jpg", frame)
    data = buffer.tobytes()

    # Send the size of the frame first
    server_socket.sendto(struct.pack("L", len(data)), server_address)
    # Send the actual frame
    server_socket.sendto(data, server_address)

cap.release()
