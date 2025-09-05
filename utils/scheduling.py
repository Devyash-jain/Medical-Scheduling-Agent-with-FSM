
from datetime import datetime, timedelta

def _parse_dt(datestr, timestr):
    return datetime.strptime(datestr + " " + timestr, "%Y-%m-%d %H:%M")

def find_contiguous_slots(df_sched, doctor, location, date_str, minutes_needed=30):
    """
    Returns a list of candidate (start_time, end_time) windows that can accommodate minutes_needed
    using 15-minute base slots.
    """
    block_size = minutes_needed // 15
    day = df_sched[(df_sched["doctor"]==doctor) & (df_sched["location"]==location) & (df_sched["date"]==date_str)]
    day = day[day["slot_status"]=="available"].sort_values(["start_time"])
    starts = day["start_time"].tolist()
    ends = day["end_time"].tolist()
    candidates = []
    for i in range(len(starts) - block_size + 1):
        ok = True
        for j in range(block_size-1):
            if starts[i+j+1] != ends[i+j]:
                ok = False
                break
        if ok:
            s = starts[i]
            e = ends[i+block_size-1]
            candidates.append((s, e))
    return candidates[:10]  # top 10 options

def reserve_slots(df_sched, doctor, location, date_str, start_time, end_time, appointment_id):
    """Marks the relevant 15-minute slots as 'booked' and attaches appointment_id."""
    # mark all rows from start_time to end_time as booked
    mask = (
        (df_sched["doctor"]==doctor) &
        (df_sched["location"]==location) &
        (df_sched["date"]==date_str)
    )
    # iterate and mark within time window
    for idx, row in df_sched[mask].iterrows():
        # row's slot is [start_time, row["end_time"]) piecewise
        if not (row["end_time"] <= start_time or row["start_time"] >= end_time):
            df_sched.at[idx, "slot_status"] = "booked"
            df_sched.at[idx, "appointment_id"] = appointment_id
    return df_sched
