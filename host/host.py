import cv2
import socket
import struct
import numpy as np

# Set up UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("192.168.2.117", 5005))

# Buffer size should match the expected frame size
MAX_DGRAM = 65507  # Same max chunk size as the slave
frame_data = b""

while True:
    # Receive the size of the incoming frame
    packed_size, _ = client_socket.recvfrom(struct.calcsize("L"))
    frame_size = struct.unpack("L", packed_size)[0]

    # Receive the actual frame data in chunks
    while len(frame_data) < frame_size:
        data, _ = client_socket.recvfrom(MAX_DGRAM)
        frame_data += data

    # Decode the frame once all chunks are received
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # Reset buffer for the next frame
    frame_data = b""

    if frame is not None:
        # Process the frame (apply any image processing here)
        processed_frame = cv2.Canny(frame, 100, 200)  # Example: Edge detection

        # Display the frame (optional)
        cv2.imshow("Processed Frame", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

client_socket.close()
cv2.destroyAllWindows()
