
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

BASE = Path(__file__).resolve().parents[1]

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def _log_message(kind, to, subject, body, attachments=None):
    outbox = BASE / "outbox"
    outbox.mkdir(exist_ok=True, parents=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = outbox / f"{kind}_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"To: {to}\nSubject: {subject}\n\n{body}\n")
        if attachments:
            f.write(f"\nAttachments: {', '.join(str(a) for a in attachments)}\n")
    return str(fname)

def send_email(to, subject, body, attachments=None):
    log_path =  _log_message("email", to, subject, body, attachments)

    if not SMTP_USER or not SMTP_PASS:
        print("⚠️ SMTP not configured, only logging to outbox.")
        return log_path

    try:
        msg = MIMEMultipart()
        msg["Form"] = SMTP_USER
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file_path in attachments:
                file_path = Path(file_path)
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition",
                                    f'attachment; filename="{file_path}"',)
                    msg.attach(part)

        with smtplib.SMTP(TP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email sent to {to}")

    except Exception as e:
        print(f"❌ Email sending failed: {e}")

    return log_path

def send_sms(to, body):
    return _log_message("sms", to, "SMS", body, attachments=None)

def send_forms(to_email):
    forms_dir = BASE / "data" / "forms"
    forms = list(forms_dir.glob("*"))
    if not forms:
        return _log_message("email", to_email, "Patient Intake Forms", "No forms attached (placeholder).")
    return _log_message("email", to_email, "Patient Intake Forms", "Please fill the attached forms.", attachments=forms)
