from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os


def generate_pdf(student_email, violations, face_path):

    os.makedirs("reports/violation_reports", exist_ok=True)

    filename = f"reports/violation_reports/report_{datetime.now().timestamp()}.pdf"

    c = canvas.Canvas(filename, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Online Examination Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, 710, f"Student Email: {student_email}")
    c.drawString(50, 690, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total = len(violations)

    c.drawString(50, 660, f"Total Violations Detected: {total}")

    if face_path:
        c.drawImage(face_path, 400, 600, width=120, height=120)

    y = 620

    if total == 0:

        c.drawString(50, y, "No violations detected during the exam.")

    else:

        c.drawString(50, y, "Violation Details:")

        y -= 30

        for i, v in enumerate(violations, 1):

            text = f"{i}. {v['type']} at {v['time']}"

            c.drawString(70, y, text)

            y -= 20

    c.save()

    return filename