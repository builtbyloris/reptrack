"""
==================== records.py ====================

This module identifies personal records (best weight, best reps)
for each exercise, and provides short motivational messages for
when a new record is set.

It does not analyze long-term trends (see progression.py) and does
not read the CSV file directly (see loader.py).
"""

MOTIVATIONAL_MESSAGES = [
    "Great work! You just beat your previous record.",
    "New personal best. That's real progress.",
    "You're moving forward. Keep building on it.",
    "Solid session - another record in the books.",
]


def personal_bests(workouts):
    """Return {exercise: best_stats} across the whole log.

    best_stats contains the highest weight lifted and the highest
    rep count recorded, each with the date it happened.
    """
    bests = {}

    for w in workouts:
        stats = bests.setdefault(w["exercise"], {
            "max_weight": None,
            "max_weight_date": None,
            "max_reps": None,
            "max_reps_date": None,
        })

        if w["weight_kg"] is not None:
            if stats["max_weight"] is None or w["weight_kg"] > stats["max_weight"]:
                stats["max_weight"] = w["weight_kg"]
                stats["max_weight_date"] = w["date"]

        if stats["max_reps"] is None or w["reps"] > stats["max_reps"]:
            stats["max_reps"] = w["reps"]
            stats["max_reps_date"] = w["date"]

    return bests


def find_new_records(sessions):
    """Walk through one exercise's sessions in date order and flag
    every session that set a new weight or rep record at the time.

    Returns a list of (session, record_type) tuples, record_type
    being "weight" or "reps".
    """
    new_records = []
    best_weight = None
    best_reps = None

    for session in sessions:
        if session["weight_kg"] is not None:
            if best_weight is None or session["weight_kg"] > best_weight:
                best_weight = session["weight_kg"]
                new_records.append((session, "weight"))

        if best_reps is None or session["reps"] > best_reps:
            best_reps = session["reps"]
            new_records.append((session, "reps"))

    return new_records


def new_record_types(previous_sessions, new_entry):
    """Compare a brand-new entry against an exercise's previous
    sessions and return which records it sets.

    Returns a list containing "weight", "reps", both, or neither
    (empty list) - used right when a workout is logged, as opposed
    to find_new_records() which replays an existing history.
    """
    record_types = []

    previous_weights = [s["weight_kg"] for s in previous_sessions if s["weight_kg"] is not None]
    if new_entry["weight_kg"] is not None:
        if not previous_weights or new_entry["weight_kg"] > max(previous_weights):
            record_types.append("weight")

    previous_reps = [s["reps"] for s in previous_sessions]
    if not previous_reps or new_entry["reps"] > max(previous_reps):
        record_types.append("reps")

    return record_types


def motivational_message(index=0):
    """Return a motivational message, cycling through the collection."""
    return MOTIVATIONAL_MESSAGES[index % len(MOTIVATIONAL_MESSAGES)]
