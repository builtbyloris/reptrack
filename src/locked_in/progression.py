"""
==================== progression.py ====================

This module analyzes how a single exercise has progressed over
time. It groups sessions by month, calculates monthly averages,
and classifies the overall trend as PROGRESSING, PLATEAU or
REGRESSING.

It does not load or clean data (see loader.py) and does not print
anything to the screen - it only returns results for menu.py to
display.
"""

from collections import defaultdict

# Below this percentage change, the trend is considered "flat"
# rather than a real improvement or drop.
PLATEAU_THRESHOLD_PERCENT = 3.0


def get_exercise_sessions(workouts, exercise_name):
    """Return every session for one exercise, sorted by date."""
    exercise_name = exercise_name.strip().title()
    sessions = [w for w in workouts if w["exercise"] == exercise_name]
    return sorted(sessions, key=lambda w: w["date"])


def monthly_averages(sessions):
    """Group sessions by calendar month and average the main metric.

    Uses weight_kg when the exercise is loaded with weight. Falls
    back to reps for bodyweight exercises (weight_kg is None), e.g.
    Pull-up, since reps is the only progression signal available.

    Returns (averages, metric) where averages is a list of
    {"month": "2026-04", "average": 61.5} dicts, sorted by month.
    """
    if not sessions:
        return [], "weight_kg"

    metric = "weight_kg" if sessions[0]["weight_kg"] is not None else "reps"

    monthly_values = defaultdict(list)
    for session in sessions:
        month_key = session["date"].strftime("%Y-%m")
        monthly_values[month_key].append(session[metric])

    averages = [
        {"month": month_key, "average": sum(values) / len(values)}
        for month_key, values in sorted(monthly_values.items())
    ]
    return averages, metric


def classify_trend(averages):
    """Classify the overall trend from a list of monthly averages.

    Compares the most recent months against the months right before
    them (not the whole history), so a plateau or regression in the
    last few weeks isn't hidden by earlier progress. This is a
    simple, transparent model - not a scientific analysis - meant to
    give an honest read on the general direction of recent training.

    Returns (status, change_percent).
    """
    if len(averages) < 2:
        return "NOT ENOUGH DATA", 0.0

    values = [a["average"] for a in averages]

    # Compare the most recent window against the window right before it.
    window = max(1, min(2, len(values) // 2))
    recent = values[-window:]
    previous = values[-2 * window:-window]
    if not previous:
        previous = values[:-window]

    recent_avg = sum(recent) / len(recent)
    earlier_avg = sum(previous) / len(previous)

    if earlier_avg == 0:
        change_percent = 0.0
    else:
        change_percent = ((recent_avg - earlier_avg) / earlier_avg) * 100

    if change_percent > PLATEAU_THRESHOLD_PERCENT:
        status = "PROGRESSING"
    elif change_percent < -PLATEAU_THRESHOLD_PERCENT:
        status = "REGRESSING"
    else:
        status = "PLATEAU"

    return status, round(change_percent, 1)
