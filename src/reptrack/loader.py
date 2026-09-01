"""
==================== loader.py ====================

This module is responsible for reading the workout log CSV file
and turning it into clean, validated Python data (a list of
dictionaries).

It does not perform any progression analysis and does not display
any CLI menus - its only job is: read the file, clean each row,
and hand back good data (plus a report of anything it had to skip).
"""

import csv
import os
from datetime import datetime

REQUIRED_COLUMNS = {"date", "exercise", "weight_kg", "reps", "sets"}

# The dataset mostly uses ISO dates, but contains at least one
# DD/MM/YYYY entry - both formats are accepted.
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def load_workouts(csv_path):
    """Read the CSV file and return (cleaned_workouts, skipped_rows).

    If the file doesn't exist yet (e.g. a fresh clone of the repo,
    or the user's real data file before their first workout), an
    empty log is created and the app simply starts with zero
    workouts - this is a normal starting state, not an error.

    Each cleaned workout is a dict with:
        date       -> datetime.date
        exercise   -> str (normalized, e.g. "Deadlift")
        weight_kg  -> float, or None for bodyweight exercises
        reps       -> int
        sets       -> int

    skipped_rows is a list of (original_row, reason) tuples for any
    row that could not be repaired, so the caller can report them
    instead of the program silently dropping data.
    """
    if not os.path.exists(csv_path):
        _create_empty_log(csv_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        if not REQUIRED_COLUMNS.issubset(fieldnames):
            missing = REQUIRED_COLUMNS - fieldnames
            raise ValueError(f"CSV is missing required column(s): {missing}")
        raw_rows = list(reader)

    # An exercise is "bodyweight" (e.g. Pull-up) only if it never has
    # a weight logged anywhere in the file. Otherwise a blank weight
    # on a normally-weighted exercise is a missing value, not a
    # bodyweight exercise, and gets skipped instead of kept as None.
    weighted_exercises = {
        (row.get("exercise") or "").strip().title()
        for row in raw_rows
        if (row.get("weight_kg") or "").strip() != ""
    }

    cleaned = []
    skipped = []
    seen_keys = set()

    for row in raw_rows:
        workout, error = _clean_row(row, weighted_exercises)

        if error:
            skipped.append((row, error))
            continue

        # Skip exact duplicate entries (same session logged twice)
        key = (workout["date"], workout["exercise"], workout["weight_kg"],
               workout["reps"], workout["sets"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        cleaned.append(workout)

    cleaned.sort(key=lambda w: w["date"])
    return cleaned, skipped


def _clean_row(row, weighted_exercises):
    """Validate and normalize a single raw CSV row.

    weighted_exercises tells us which exercise names are ever logged
    with a weight elsewhere in the file, so we can tell a genuine
    bodyweight exercise (always blank, e.g. Pull-up) apart from a
    missing weight value on an exercise that should have one.

    Returns (workout_dict, None) if the row is usable, or
    (None, reason) if it has to be skipped.
    """
    exercise = (row.get("exercise") or "").strip().title()
    if not exercise:
        return None, "missing exercise name"

    date = _parse_date((row.get("date") or "").strip())
    if date is None:
        return None, f"unparseable date '{row.get('date')}'"

    reps = _parse_int(row.get("reps"))
    if reps is None or reps <= 0:
        return None, f"invalid reps value '{row.get('reps')}'"

    sets = _parse_int(row.get("sets"))
    if sets is None or sets <= 0:
        return None, f"invalid sets value '{row.get('sets')}'"

    weight_raw = (row.get("weight_kg") or "").strip()
    if weight_raw == "":
        if exercise in weighted_exercises:
            return None, f"missing weight value for '{exercise}'"
        weight = None  # genuine bodyweight exercise, e.g. Pull-up
    else:
        weight = _parse_float(weight_raw)
        if weight is None or weight <= 0:
            return None, f"invalid weight value '{row.get('weight_kg')}'"

    workout = {
        "date": date,
        "exercise": exercise,
        "weight_kg": weight,
        "reps": reps,
        "sets": sets,
    }
    return workout, None


def _create_empty_log(csv_path):
    """Create a fresh workout log with just the header row."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "exercise", "weight_kg", "reps", "sets"])


def _parse_date(value):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
