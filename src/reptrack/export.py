"""
==================== export.py ====================

This module exports whatever workouts are currently in memory to a
timestamped CSV file, e.g. for backing up or sharing progress data.

It does not load, clean or analyze data - it only writes out the
same in-memory list every other module already uses.
"""

import csv
import os
from datetime import datetime


def export_workouts(workouts, export_dir):
    """Write all workouts to a new timestamped CSV file in export_dir.

    Returns the path of the created file, or None if there was
    nothing to export yet.
    """
    if not workouts:
        return None

    os.makedirs(export_dir, exist_ok=True)
    filename = f"workout_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    export_path = os.path.join(export_dir, filename)

    with open(export_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "exercise", "weight_kg", "reps", "sets"])
        for w in sorted(workouts, key=lambda w: w["date"]):
            weight_value = w["weight_kg"] if w["weight_kg"] is not None else ""
            writer.writerow([
                w["date"].isoformat(), w["exercise"], weight_value, w["reps"], w["sets"]
            ])

    return export_path
