import cv2
from monitoring.voilation_logger import log_violation


def detect_violations():

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Example condition
        key = cv2.waitKey(1)

        if key == ord('v'):
            log_violation("Looking Away From Screen")

        if key == ord('p'):
            log_violation("Phone Usage Detected")

        cv2.imshow("Monitoring", frame)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()