import smtplib
from email.message import EmailMessage


SENDER_EMAIL = "22eg112b54@anurag.edu.in"
APP_PASSWORD = "wnsfmgcrdvvivnmj"


def send_email_with_attachment(to_email, subject, body, pdf_path):

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.set_content(body)

    with open(pdf_path, "rb") as f:
        file_data = f.read()

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="pdf",
        filename="Exam_Report.pdf"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)