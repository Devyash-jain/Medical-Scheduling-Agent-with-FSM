
# Re-generates patients.csv and doctor_schedules.{csv,xlsx}
# Run: python scripts/generate_data.py
import csv, random, string
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd

BASE = Path(__file__).resolve().parents[1]

first_names = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Muhammad","Ishaan","Kabir",
               "Anaya","Aadhya","Aarohi","Diya","Myra","Aanya","Anika","Navya","Sara","Pari"]
last_names = ["Sharma","Verma","Patel","Mehta","Reddy","Gupta","Singh","Nair","Iyer","Dutta","Ghosh","Khan","Kapoor"]
insurers = ["Aetna","Cigna","United Healthcare","Blue Cross","Care Health","Niva Bupa","HDFC Ergo"]
locations = ["Koramangala","Indiranagar","Whitefield"]
doctors = [
    {"doctor_id":"D001","doctor":"Dr. Meera Shah","specialty":"Cardiology","location":"Koramangala"},
    {"doctor_id":"D002","doctor":"Dr. Arjun Patel","specialty":"General Medicine","location":"Indiranagar"},
    {"doctor_id":"D003","doctor":"Dr. Priya Rao","specialty":"Dermatology","location":"Whitefield"},
]

def rand_phone():
    return "9" + "".join(random.choices(string.digits, k=9))

def rand_email(first, last):
    domains = ["example.com","mail.com","inbox.com"]
    return f"{first.lower()}.{last.lower()}@{random.choice(domains)}"

def rand_dob(start_year=1955, end_year=2010):
    y = random.randint(start_year, end_year)
    m = random.randint(1,12)
    d = random.randint(1,28)
    return date(y,m,d)

def rand_member_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

def rand_group_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

random.seed(42)

# Patients
rows = []
for i in range(1, 51):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    dob = rand_dob()
    email = rand_email(fn, ln)
    phone = rand_phone()
    pref_doc = random.choice(doctors)["doctor"]
    loc = random.choice(locations)
    insurer = random.choice(insurers)
    last_visit = None
    if random.random() < 0.65:
        last_visit = date.today() - timedelta(days=random.randint(30, 730))
    returning = bool(last_visit)
    rows.append({
        "patient_id": f"P{i:03d}",
        "first_name": fn,
        "last_name": ln,
        "dob": dob.isoformat(),
        "email": email,
        "phone": phone,
        "preferred_doctor": pref_doc,
        "location": loc,
        "insurance_carrier": insurer,
        "insurance_member_id": rand_member_id(),
        "insurance_group_id": rand_group_id(),
        "last_visit_date": last_visit.isoformat() if last_visit else "",
        "is_returning": "Y" if returning else "N"
    })
patients_csv = BASE / "data" / "patients.csv"
with open(patients_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

# Schedules
start_date = date.today()
days = [start_date + timedelta(days=i) for i in range(0, 30)]
def day_slots():
    slots = []
    t = datetime.combine(date.today(), datetime.strptime("10:00","%H:%M").time())
    end1 = datetime.combine(date.today(), datetime.strptime("13:00","%H:%M").time())
    while t < end1:
        slots.append((t.time().strftime("%H:%M"), (t+timedelta(minutes=15)).time().strftime("%H:%M")))
        t += timedelta(minutes=15)
    t = datetime.combine(date.today(), datetime.strptime("14:00","%H:%M").time())
    end2 = datetime.combine(date.today(), datetime.strptime("17:00","%H:%M").time())
    while t < end2:
        slots.append((t.time().strftime("%H:%M"), (t+timedelta(minutes=15)).time().strftime("%H:%M")))
        t += timedelta(minutes=15)
    return slots

sched_rows = []
for d in doctors:
    for dy in days:
        for st, et in day_slots():
            sched_rows.append({
                "doctor_id": d["doctor_id"],
                "doctor": d["doctor"],
                "location": d["location"],
                "date": dy.isoformat(),
                "start_time": st,
                "end_time": et,
                "slot_status": "available",
                "appointment_id": ""
            })

csvp = BASE / "data" / "doctor_schedules.csv"
with open(csvp, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(sched_rows[0].keys()))
    writer.writeheader()
    writer.writerows(sched_rows)

df = pd.DataFrame(sched_rows)
try:
    with pd.ExcelWriter(BASE / "data" / "doctor_schedules.xlsx") as writer:
        df.to_excel(writer, sheet_name="schedules", index=False)
except Exception:
    pass

print("Datasets regenerated.")
