
import os
from pathlib import Path
from datetime import datetime
import csv

try:
    import pandas as pd
except Exception:
    pd = None

BASE = Path(__file__).resolve().parents[1]

def load_patients():
    path = BASE / "data" / "patients.csv"
    if pd is None:
        # minimal csv reader
        import csv
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [r for r in reader]
    else:
        return pd.read_csv(path)

def save_patients(df_or_list):
    path = BASE / "data" / "patients.csv"
    if pd is None:
        # not implemented; project expects pandas for write
        raise RuntimeError("Pandas required to write patients.csv")
    df_or_list.to_csv(path, index=False)

def load_schedule():
    # Prefer Excel if available
    xlsx = BASE / "data" / "doctor_schedules.xlsx"
    csvp = BASE / "data" / "doctor_schedules.csv"
    if pd is None:
        # Fallback to csv
        import csv
        with open(csvp, newline="", encoding="utf-8") as f:
            return [r for r in csv.DictReader(f)]
    else:
        if xlsx.exists():
            return pd.read_excel(xlsx, sheet_name="schedules")
        return pd.read_csv(csvp)

def save_schedule(df):
    xlsx = BASE / "data" / "doctor_schedules.xlsx"
    csvp = BASE / "data" / "doctor_schedules.csv"
    if pd is None:
        # write csv only
        import csv
        with open(csvp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(df[0].keys()))
            writer.writeheader()
            writer.writerows(df)
    else:
        # write both for convenience
        df.to_csv(csvp, index=False)
        try:
            with pd.ExcelWriter(xlsx) as writer:
                df.to_excel(writer, sheet_name="schedules", index=False)
        except Exception:
            pass

def export_admin_report(appointments_df, reminders_df):
    """Export multi-sheet Excel report into /outbox for admin review."""
    out_dir = BASE / "outbox"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    xlsx_path = out_dir / f"admin_report_{ts}.xlsx"
    if pd is None:
        # csv fallbacks
        appointments_df.to_csv(out_dir / f"appointments_{ts}.csv", index=False)
        reminders_df.to_csv(out_dir / f"reminders_{ts}.csv", index=False)
        return str(xlsx_path)
    else:
        try:
            with pd.ExcelWriter(xlsx_path) as writer:
                appointments_df.to_excel(writer, sheet_name="appointments", index=False)
                reminders_df.to_excel(writer, sheet_name="reminders", index=False)
        except Exception:
            # if Excel fails, write CSVs
            appointments_df.to_csv(out_dir / f"appointments_{ts}.csv", index=False)
            reminders_df.to_csv(out_dir / f"reminders_{ts}.csv", index=False)
    return str(xlsx_path)
