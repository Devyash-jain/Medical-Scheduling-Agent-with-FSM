# Medical-Scheduling-Agent-with-FSM
This repo contains a minimal, runnable demo to satisfy the requirements: greeting, patient lookup, smart scheduling, calendar simulation, insurance capture, confirmation, form distribution, reminders, and admin Excel export.

## Quickstart
```
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## What it demonstrates
* Patient Greeting & Lookup from CSV (synthetic EMR of 50 patients).
* Smart Scheduling: 60 min for new; 30 min for returning. Finds contiguous 15-min slots.
* Calendar Integration simulated via an Excel/CSV schedule; reservations mark rows as booked.
* Insurance Capture: carrier/member/group fields.
* Confirmation: Logs Email/SMS into outbox and send email to user. (use Twilio if desired for SMS).
* Form Distribution: Sends placeholder forms from data/forms/.
* Reminders: Creates T-72h, T-48h, T-24h entries with required actions.
* Admin Report: Exports Excel with appointments + reminders for review.

## Data
* data/patients.csv — 50 synthetic patients.
* data/doctor_schedules.csv (+ .xlsx) — next 7 days, 10:00–13:00 & 14:00–17:00, 15-min slots across 3 doctors.

## Notes
* This is intentionally self-contained to make the demo easy to run and record.
* You can swap the rule-based flow with LangChain/LangGraph later; the UI/API boundaries are kept simple.
* Update venv via cmd as:
  * $env:SMTP_SERVER="smtp.gmail.com".
  * $env:SMTP_PORT="587".
  * $env:SMTP_USER=your email for sending mails.
  * $env:SMTP_PASS=your generated password for email usage via your Google Acoount -> App Passwords.
