
import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd

from utils.data_io import load_patients, load_schedule, save_schedule, export_admin_report
from utils.scheduling import find_contiguous_slots, reserve_slots
from utils.comms import send_email, send_sms, send_forms

st.set_page_config(page_title="RagaAI - Medical Scheduling Agent (Demo)", layout="centered")

st.title("🩺 AI Scheduling Agent — Demo")

st.markdown("This demo walks through greeting → patient lookup → smart scheduling → insurance collection → confirmation → forms → reminders.")

# Load data
patients = load_patients()
if isinstance(patients, list):
    import pandas as _pd
    patients_df = _pd.DataFrame(patients)
else:
    patients_df = patients

schedule = load_schedule()
if isinstance(schedule, list):
    import pandas as _pd
    sched_df = _pd.DataFrame(schedule)
else:
    sched_df = schedule

# Session state
if "state" not in st.session_state:
    st.session_state.state = {
        "patient_found": False,
        "patient_record": None,
        "appointment": {},
        "reminders": []
    }

with st.form("patient_form"):
    st.subheader("1) Patient Greeting & Intake")
    name = st.text_input("Patient Full Name")
    dob = st.date_input("Date of Birth", value=date(1995,1,1))
    preferred_doctor = st.selectbox("Doctor", sorted(sched_df["doctor"].unique().tolist()))
    location = st.selectbox("Location", sorted(sched_df["location"].unique().tolist()))
    submitted = st.form_submit_button("Lookup Patient")
    if submitted:
        # Simple lookup: name + dob match
        fn = name.split()[0].strip().lower() if name else ""
        ln = name.split()[-1].strip().lower() if name else ""
        dob_str = dob.isoformat()
        mask = (
            (patients_df["first_name"].str.lower()==fn) &
            (patients_df["last_name"].str.lower()==ln) &
            (patients_df["dob"]==dob_str)
        )
        if mask.any():
            st.session_state.state["patient_found"] = True
            st.session_state.state["patient_record"] = patients_df[mask].iloc[0].to_dict()
            st.success("Returning patient detected.")
        else:
            # create a lightweight new record in-memory; will finalize on confirmation
            st.session_state.state["patient_found"] = False
            st.session_state.state["patient_record"] = {
                "patient_id": f"TMP-{int(datetime.now().timestamp())}",
                "first_name": fn.title(),
                "last_name": ln.title(),
                "dob": dob_str,
                "email": "",
                "phone": "",
                "preferred_doctor": preferred_doctor,
                "location": location,
                "insurance_carrier": "",
                "insurance_member_id": "",
                "insurance_group_id": "",
                "last_visit_date": "",
                "is_returning": "N"
            }
            st.info("New patient. We'll collect additional details below.")

if st.session_state.state["patient_record"]:
    pr = st.session_state.state["patient_record"]
    st.subheader("2) Smart Scheduling")
    is_returning = pr.get("is_returning","N") == "Y"
    minutes_needed = 30 if is_returning else 60
    st.caption(f"Appointment length based on patient type: **{minutes_needed} minutes**.")
    date_choice = st.date_input("Desired Date", value=date.today())
    candidates = find_contiguous_slots(sched_df, preferred_doctor, location, date_choice.isoformat(), minutes_needed=minutes_needed)
    if candidates:
        label_options = [f"{c[0]}–{c[1]}" for c in candidates]
        pick = st.selectbox("Available Slots", label_options, index=0)
        if st.button("Reserve Selected Slot"):
            start_time, end_time = pick.split("–")
            appt_id = f"A{int(datetime.now().timestamp())}"
            sched_df = reserve_slots(sched_df, preferred_doctor, location, date_choice.isoformat(), start_time, end_time, appt_id)
            save_schedule(sched_df)
            st.session_state.state["appointment"] = {
                "appointment_id": appt_id,
                "patient_id": pr["patient_id"],
                "name": f"{pr['first_name']} {pr['last_name']}",
                "doctor": preferred_doctor,
                "location": location,
                "date": date_choice.isoformat(),
                "start_time": start_time,
                "end_time": end_time,
                "duration_min": minutes_needed,
            }
            st.success(f"Reserved {start_time}–{end_time} on {date_choice.isoformat()} with {preferred_doctor}.")

    if not candidates and minutes_needed == 60:
        st.warning("No 60-min slots available. Showing 30-min options instead.")
        candidates = find_contiguous_slots(
            sched_df, preferred_doctor, location, date_choice.isoformat(),
            minutes_needed=30
        )

    st.subheader("3) Insurance Collection")
    col1, col2, col3 = st.columns(3)
    with col1:
        carrier = st.text_input("Carrier", value=pr.get("insurance_carrier",""))
    with col2:
        member_id = st.text_input("Member ID", value=pr.get("insurance_member_id",""))
    with col3:
        group_id = st.text_input("Group ID", value=pr.get("insurance_group_id",""))

    st.subheader("4) Confirmation & Messaging")
    email = st.text_input("Email", value=pr.get("email",""))
    phone = st.text_input("Phone", value=pr.get("phone",""))
    if st.button("Confirm Appointment + Send Email/SMS"):
        appt = st.session_state.state["appointment"]
        if not appt:
            st.error("Please reserve a slot first.")
        else:
            # build confirmation content
            subject = f"Appointment Confirmation — {appt['appointment_id']}"
            body = (
                f"Dear {appt['name']},\n\n"
                f"Your appointment is confirmed with {appt['doctor']} at {appt['location']} on {appt['date']} "
                f"from {appt['start_time']} to {appt['end_time']}.\n\n"
                "Thank you."
            )
            email_log = send_email(email or "test@example.com", subject, body)
            sms_log = send_sms(phone or "9999999999", f"Appt {appt['appointment_id']} on {appt['date']} {appt['start_time']} confirmed.")
            st.success("Confirmation sent (logged to outbox).")
            st.code(email_log)
            st.code(sms_log)
            # send forms
            if st.button("Send Intake Forms"):
                forms_log = send_forms(email or "test@example.com")
                st.success("Forms dispatched (logged).")
                st.code(forms_log)

    st.subheader("5) Reminder System (Simulated)")
    st.caption("Creates 3 reminders: T-72h (plain), T-48h (with actions), T-24h (with actions).")
    if st.button("Schedule Reminders"):
        appt = st.session_state.state["appointment"]
        if not appt:
            st.error("No appointment reserved yet.")
        else:
            appt_dt = datetime.strptime(appt["date"] + " " + appt["start_time"], "%Y-%m-%d %H:%M")
            reminder_offsets = [timedelta(hours=72), timedelta(hours=48), timedelta(hours=24)]
            reminders = []
            for i, off in enumerate(reminder_offsets, start=1):
                when = appt_dt - off
                msg = "Reminder: Upcoming visit."
                if i in (2,3):
                    msg += " Reply with (1) Filled forms? (2) Confirm visit? If cancel, share reason."
                reminders.append({
                    "appointment_id": appt["appointment_id"],
                    "send_at": when.isoformat(timespec="minutes"),
                    "channel": "email+sms",
                    "message": msg
                })
            st.session_state.state["reminders"] = reminders
            st.dataframe(pd.DataFrame(reminders))
            for r in reminders:
                send_email(
                    to=email or "test@example.com",
                    subject=f"Reminder — {r['appointment_id']}",
                    body=r["message"]
                )

    st.subheader("6) Export Admin Report")
    if st.button("Export Excel Report"):
        import pandas as _pd
        appt = st.session_state.state["appointment"]
        appt_df = _pd.DataFrame([appt]) if appt else _pd.DataFrame(columns=["appointment_id"])
        rem_df = _pd.DataFrame(st.session_state.state["reminders"])
        path = export_admin_report(appt_df, rem_df)
        st.success("Report generated.")
        st.code(path)

st.divider()
st.markdown("**Notes:** This is a local demo using CSV/Excel to simulate EMR and calendar. Email/SMS are logged to the `outbox/` folder.")
