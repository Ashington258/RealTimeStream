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

# Define max packet size (e.g., 60KB)
MAX_DGRAM = 65507  # UDP max packet size is 65507 bytes

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode the frame as JPEG to reduce data size
    ret, buffer = cv2.imencode(".jpg", frame)
    data = buffer.tobytes()

    # Send the size of the frame first
    server_socket.sendto(struct.pack("L", len(data)), server_address)

    # Split data into chunks and send each one
    for i in range(0, len(data), MAX_DGRAM):
        chunk = data[i : i + MAX_DGRAM]
        server_socket.sendto(chunk, server_address)

cap.release()
