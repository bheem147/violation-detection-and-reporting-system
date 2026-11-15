import cv2
from datetime import datetime
import os

def capture_face(frame):

    os.makedirs("snapshots/faces", exist_ok=True)

    filename = f"snapshots/faces/candidate_{datetime.now().timestamp()}.jpg"

    cv2.imwrite(filename, frame)

    return filename