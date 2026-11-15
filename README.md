## Online Exam Monitoring System

A web-based online exam monitoring system built with **Flask**, **OpenCV**, and **MediaPipe**.  
It shows a **live camera feed** on the dashboard, detects violations in real time, captures a candidate snapshot at exam start, generates a PDF report, and emails it to the student when the exam ends.

### Features

- **Dashboard** with real-time webcam feed in the browser
- **Start Exam** / **End Exam** buttons; student email input for the report
- **Automatic violation detection** (no separate script needed):
  - **Candidate not visible** — no face detected for a sustained period
  - **Multiple persons detected** — more than one face in frame
  - **Looking away from screen** — face turned away (side profile) for a sustained period
  - **Phone usage detected** — hand (or phone) visible anywhere in the frame
- PDF report with violation list and face snapshot, sent via email to the student

### Project Structure

| Path | Description |
|------|-------------|
| **app.py** | Flask app: dashboard, `/video_feed` (live stream), `/start_exam`, `/stop_exam`, and real-time violation detection (OpenCV + MediaPipe) |
| **templates/index.html** | Dashboard UI: live camera frame, email field, Start Exam / End Exam buttons |
| **monitoring/voilation_logger.py** | In-memory storage for violations |
| **monitoring/face_capture.py** | Saves candidate snapshot to `snapshots/faces/` |
| **monitoring/monitoring_system.py** | Optional standalone script (key-based violation logging); not required when using the dashboard |
| **services/pdf_report.py** | Generates PDF report with violations and snapshot in `reports/violation_reports/` |
| **services/email_service.py** | Sends the PDF report via Gmail |
| **requirements.txt** | Python dependencies (Flask, OpenCV, MediaPipe, ReportLab, etc.) |

### Prerequisites

- **Python 3.8+**
- **Webcam** (used by OpenCV for the live feed and snapshot)
- **Gmail account** with an [App Password](https://support.google.com/accounts/answer/185833) for sending email

### Setup

1. **Create and activate a virtual environment (optional but recommended)**:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure email** in `services/email_service.py`:

   ```python
   SENDER_EMAIL = "your_gmail@gmail.com"
   APP_PASSWORD = "your_gmail_app_password"
   ```

### Running the System

1. **Start the Flask server**:

   ```bash
   python app.py
   ```

   The app runs at **http://127.0.0.1:5000** by default.

2. **Open the dashboard** in a browser:

   ```
   http://127.0.0.1:5000/
   ```

3. **On the dashboard**:
   - You’ll see the **live camera feed** (candidate view).
   - Enter the **student email** (used for the report).
   - Click **Start Exam** — captures a face snapshot and starts counting violations.
   - Keep the page open; the app detects violations in real time (candidate not visible, multiple persons, looking away, hand/phone in frame).
   - When done, click **End Exam** — a PDF is generated with all violations and the snapshot, then emailed to the student.

### Violations Detected

| Violation | Trigger |
|-----------|--------|
| Candidate not visible | No face detected for a sustained period |
| Multiple persons detected | More than one face in frame for a sustained period |
| Looking away from screen | Single face in strong profile (turned away) for a sustained period |
| Phone usage detected | Hand (or phone) visible anywhere in the frame for a sustained period |

All violations are listed in the PDF report and included in the email.

### Notes

- Snapshots are saved under **`snapshots/faces/`**.
- PDF reports are saved under **`reports/violation_reports/`**.

