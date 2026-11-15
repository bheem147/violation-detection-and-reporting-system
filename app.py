from flask import Flask, request, render_template, Response
from monitoring.voilation_logger import get_violations, clear_violations, log_violation
from monitoring.face_capture import capture_face
from services.pdf_report import generate_pdf
from services.email_service import send_email_with_attachment
import cv2
import mediapipe as mp

app = Flask(__name__)

face_snapshot_path = None
video_capture = cv2.VideoCapture(0)
last_frame = None

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

no_face_frames = 0
multi_face_frames = 0
looking_away_frames = 0
phone_usage_frames = 0

NO_FACE_THRESHOLD = 60
MULTI_FACE_THRESHOLD = 60
LOOKING_AWAY_THRESHOLD = 60
PHONE_USAGE_THRESHOLD = 20


def is_hand_in_frame(frame):
    """Detect if a hand (proxy for phone / object) is visible anywhere in the frame."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    return results.multi_hand_landmarks is not None and len(results.multi_hand_landmarks) > 0


def analyze_frame_for_violations(frame):
    """
    Heuristic-based violation detection:
    - No face detected for a while -> candidate not visible
    - Multiple faces detected for a while -> multiple persons detected
    - Single face turned away (very narrow profile) -> looking away from screen
    - Hand visible anywhere in frame (proxy for phone/object) -> phone usage detected
    """
    global no_face_frames, multi_face_frames, looking_away_frames, phone_usage_frames

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
    )

    num_faces = len(faces)

    if num_faces == 0:
        no_face_frames += 1
        multi_face_frames = 0
        looking_away_frames = 0
        phone_usage_frames = 0

        if no_face_frames == NO_FACE_THRESHOLD:
            log_violation("Candidate not visible")

    elif num_faces > 1:
        multi_face_frames += 1
        no_face_frames = 0
        looking_away_frames = 0

        if multi_face_frames == MULTI_FACE_THRESHOLD:
            log_violation("Multiple persons detected")

        if is_hand_in_frame(frame):
            phone_usage_frames += 1
        else:
            phone_usage_frames = 0

        if phone_usage_frames == PHONE_USAGE_THRESHOLD:
            log_violation("Phone usage detected")

    else:
        no_face_frames = 0
        multi_face_frames = 0

        (x, y, w, h) = faces[0]
        aspect_ratio = w / float(h)

        if aspect_ratio < 0.5:
            looking_away_frames += 1
        else:
            looking_away_frames = 0

        if looking_away_frames == LOOKING_AWAY_THRESHOLD:
            log_violation("Looking away from screen")

        if is_hand_in_frame(frame):
            phone_usage_frames += 1
        else:
            phone_usage_frames = 0

        if phone_usage_frames == PHONE_USAGE_THRESHOLD:
            log_violation("Phone usage detected")


def gen_frames():
    global last_frame

    while True:
        success, frame = video_capture.read()

        if not success:
            break

        last_frame = frame.copy()

        analyze_frame_for_violations(frame)

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/start_exam", methods=["POST"])
def start_exam():

    global face_snapshot_path, last_frame, no_face_frames, multi_face_frames, looking_away_frames, phone_usage_frames

    no_face_frames = 0
    multi_face_frames = 0
    looking_away_frames = 0
    phone_usage_frames = 0
    clear_violations()

    frame = last_frame

    if frame is None:

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()

        if ret:
            face_snapshot_path = capture_face(frame)

        cap.release()

    else:

        face_snapshot_path = capture_face(frame)

    return "Exam Started"


@app.route("/stop_exam", methods=["POST"])
def stop_exam():

    student_email = request.form.get("email")

    violations = get_violations()

    pdf_path = generate_pdf(student_email, violations, face_snapshot_path)

    if len(violations) > 0:

        subject = "Online Exam Violation Report"

        body = """
Violations were detected during your online exam.

Please check the attached report for full details.
"""

    else:

        subject = "Exam Completion Report"

        body = """
Your exam was completed successfully.

No violations were detected.
"""

    send_email_with_attachment(
        student_email,
        subject,
        body,
        pdf_path
    )

    clear_violations()

    return "Exam Completed and Report Sent"


if __name__ == "__main__":
    app.run(debug=True)