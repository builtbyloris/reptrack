"""
==================== entry.py ====================

This module lets the user log a brand-new workout from the CLI. It
validates the input using the same rules as loader.py, appends the
entry to the CSV file on disk so the log grows over time, and uses
records.py to tell the user whether it's a new personal record.

It does not display the main menu and does not perform trend
analysis - it only handles adding a single new entry.
"""

import csv
from datetime import date, datetime

from locked_in import records

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def add_workout(workouts, csv_path):
    """Interactively collect one new workout, save it, and report
    back whether it set a new personal record.

    Appends the entry to both the in-memory `workouts` list (so the
    rest of the session sees it immediately) and to the CSV file.
    """
    exercise = input("Exercise: ").strip().title()
    if not exercise:
        print("Exercise name can't be empty.\n")
        return

    previous_sessions = [w for w in workouts if w["exercise"] == exercise]
    is_bodyweight = bool(previous_sessions) and not any(
        s["weight_kg"] is not None for s in previous_sessions
    )

    weight = None
    if not is_bodyweight:
        weight_raw = input("Weight in kg (leave blank if bodyweight): ").strip()
        if weight_raw:
            weight = _parse_positive_float(weight_raw)
            if weight is None:
                print("Invalid weight value - workout not saved.\n")
                return
        elif previous_sessions:
            print("This exercise is usually logged with a weight - workout not saved.\n")
            return

    reps = _parse_positive_int(input("Reps: ").strip())
    if reps is None:
        print("Invalid reps value - workout not saved.\n")
        return

    sets = _parse_positive_int(input("Sets: ").strip())
    if sets is None:
        print("Invalid sets value - workout not saved.\n")
        return

    date_raw = input("Date (YYYY-MM-DD, leave blank for today): ").strip()
    entry_date = date.today() if not date_raw else _parse_date(date_raw)
    if entry_date is None:
        print("Invalid date value - workout not saved.\n")
        return

    new_entry = {
        "date": entry_date,
        "exercise": exercise,
        "weight_kg": weight,
        "reps": reps,
        "sets": sets,
    }

    record_types = records.new_record_types(previous_sessions, new_entry)

    workouts.append(new_entry)
    _append_to_csv(csv_path, new_entry)

    print("\nWorkout saved.")
    if record_types:
        label = " and ".join(record_types)
        print(f"NEW PERSONAL RECORD! ({label})")
        print(records.motivational_message(len(record_types)))
    print()


def _append_to_csv(csv_path, entry):
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        weight_value = entry["weight_kg"] if entry["weight_kg"] is not None else ""
        writer.writerow([
            entry["date"].isoformat(),
            entry["exercise"],
            weight_value,
            entry["reps"],
            entry["sets"],
        ])


def _parse_positive_float(value):
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _parse_positive_int(value):
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _parse_date(value):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
