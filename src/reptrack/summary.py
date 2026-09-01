"""
==================== summary.py ====================

This module builds the views that span multiple exercises at once:
the overall progress summary (counts of workouts, personal bests,
plateaus, regressions) and a side-by-side comparison between two
exercises.

It combines results from progression.py and records.py rather than
recalculating anything itself, and it does not load, clean or store
workout data - see loader.py and entry.py for that.
"""

from locked_in import progression, records


def build_summary(workouts):
    """Return the overall stats used for the progress summary.

    With zero workouts logged, every count is naturally 0 - there
    is no special-case logic needed for the empty state.
    """
    exercises = sorted({w["exercise"] for w in workouts})
    bests = records.personal_bests(workouts)

    plateau_count = 0
    regression_count = 0
    for exercise in exercises:
        sessions = progression.get_exercise_sessions(workouts, exercise)
        averages, _ = progression.monthly_averages(sessions)
        status, _ = progression.classify_trend(averages)
        if status == "PLATEAU":
            plateau_count += 1
        elif status == "REGRESSING":
            regression_count += 1

    return {
        "workouts": len(workouts),
        "exercises_tracked": len(exercises),
        "personal_bests": len(bests),
        "plateaus_detected": plateau_count,
        "regressions_detected": regression_count,
    }


def compare_exercises(workouts, exercise_a, exercise_b):
    """Return comparable stats for two exercises.

    Returns a dict keyed by exercise name; the value is None for an
    exercise with no logged sessions, so the caller can report that
    instead of guessing or crashing.
    """
    bests = records.personal_bests(workouts)
    result = {}

    for exercise in (exercise_a, exercise_b):
        sessions = progression.get_exercise_sessions(workouts, exercise)
        if not sessions:
            result[exercise] = None
            continue

        averages, metric = progression.monthly_averages(sessions)
        status, change_percent = progression.classify_trend(averages)
        exercise_bests = bests.get(exercise, {})

        result[exercise] = {
            "sessions": len(sessions),
            "metric": metric,
            "status": status,
            "change_percent": change_percent,
            "best_weight": exercise_bests.get("max_weight"),
            "best_reps": exercise_bests.get("max_reps"),
        }

    return result
