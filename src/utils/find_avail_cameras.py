import cv2


def check_cameras():
    """Check which camera ports are available"""
    for i in range(10):  # Check first 10 ports
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera port {i} is available")
            ret, frame = cap.read()
            if ret:
                print(f"  Successfully grabbed frame from port {i}")
            else:
                print(f"  Could not grab frame from port {i}")
            cap.release()
        else:
            print(f"Camera port {i} is not available")


if __name__ == "__main__":
    check_cameras()
