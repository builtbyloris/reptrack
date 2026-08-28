"""
==================== menu.py ====================

This module is the command-line interface: it displays the menu,
reads user input and calls into the other modules to show results.

It does not implement any analysis logic itself - all calculations
live in progression.py, records.py, summary.py and export.py. The
menu only routes choices and formats output, and it always checks
whether there's any data before asking for more input, so an empty
log never causes a crash or a confusing question.
"""

from locked_in import entry, export, profile, progression, records, summary

MENU_TEXT = """
========================================
             LOCKED-IN
       Workout Progress Tracker
========================================
1. Show progression for an exercise
2. Show personal bests
3. Check for plateaus
4. Check for regressions
5. Log a new workout
6. View / update profile
7. View workout history
8. Compare exercises
9. View progress summary
10. Export workout data
0. Exit
"""


def run(workouts, csv_path, user_profile, profile_path, export_dir):
    """Start the interactive CLI loop."""
    print(f"Loaded {len(workouts)} workout entries.")

    while True:
        print(MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "1":
            show_progression(workouts)
        elif choice == "2":
            show_personal_bests(workouts)
        elif choice == "3":
            show_by_status(workouts, "PLATEAU")
        elif choice == "4":
            show_by_status(workouts, "REGRESSING")
        elif choice == "5":
            entry.add_workout(workouts, csv_path)
        elif choice == "6":
            user_profile = show_profile(user_profile, profile_path)
        elif choice == "7":
            show_history(workouts)
        elif choice == "8":
            show_comparison(workouts)
        elif choice == "9":
            show_summary(workouts)
        elif choice == "10":
            show_export(workouts, export_dir)
        elif choice == "0":
            print("See you at the next session.")
            break
        else:
            print("Invalid option, please choose one of the numbers shown.\n")


def _available_exercises(workouts):
    return sorted({w["exercise"] for w in workouts})


def show_progression(workouts):
    exercises = _available_exercises(workouts)
    if not exercises:
        print("\nNo workouts logged yet. Use option 5 to log your first workout.\n")
        return

    print("\nAvailable exercises:", ", ".join(exercises))
    name = input("Which exercise? ").strip()

    sessions = progression.get_exercise_sessions(workouts, name)
    if not sessions:
        print(f"\nNo data found for '{name}'.\n")
        return

    averages, metric = progression.monthly_averages(sessions)
    status, change_percent = progression.classify_trend(averages)
    unit = "kg" if metric == "weight_kg" else "reps"

    print(f"\n{sessions[0]['exercise']} progression:")
    for a in averages:
        print(f"{_format_month(a['month'])}: avg {a['average']:.1f} {unit}")

    if status == "NOT ENOUGH DATA":
        print("Trend: not enough data yet to tell.\n")
    else:
        sign = "+" if change_percent >= 0 else ""
        print(f"Trend: {status.title()} ({sign}{change_percent}% over the period)\n")

    _report_latest_record(sessions)


def _report_latest_record(sessions):
    """If the most recent session set a new record, announce it."""
    new_records = records.find_new_records(sessions)
    if not new_records:
        return

    last_session, record_type = new_records[-1]
    if last_session["date"] != sessions[-1]["date"]:
        return  # the most recent session did not set a record

    label = "weight" if record_type == "weight" else "reps"
    print(f"NEW PERSONAL RECORD! ({label})")
    print(records.motivational_message(len(new_records)))
    print()


def show_personal_bests(workouts):
    bests = records.personal_bests(workouts)
    if not bests:
        print("\nNo personal bests yet - log a workout first.\n")
        return

    print("\nPersonal bests:")
    for exercise, stats in sorted(bests.items()):
        parts = []
        if stats["max_weight"] is not None:
            parts.append(f"{stats['max_weight']:g} kg (on {stats['max_weight_date']})")
        parts.append(f"{stats['max_reps']} reps (on {stats['max_reps_date']})")
        print(f"- {exercise}: " + " | ".join(parts))
    print()


def show_by_status(workouts, target_status):
    exercises = _available_exercises(workouts)
    label = "plateaus" if target_status == "PLATEAU" else "regressions"

    if not exercises:
        print(f"\nNot enough data yet to check for {label}. Log a few workouts first.\n")
        return

    matches = []
    for exercise in exercises:
        sessions = progression.get_exercise_sessions(workouts, exercise)
        averages, _ = progression.monthly_averages(sessions)
        status, change_percent = progression.classify_trend(averages)
        if status == target_status:
            matches.append((exercise, change_percent))

    print(f"\nExercises with detected {label}:")
    if not matches:
        print("None found - nice.")
    for exercise, change_percent in matches:
        print(f"- {exercise} ({change_percent}%)")
    print()


def show_profile(user_profile, profile_path):
    """Display the current profile and offer to update it.

    Returns the (possibly updated) profile so the caller keeps a
    fresh copy for the rest of the session.
    """
    print("\nYour profile:")
    for field in ("name", "age", "sex", "goal", "created_on"):
        value = user_profile.get(field) or "-"
        print(f"- {field.replace('_', ' ').title()}: {value}")

    choice = input("\nUpdate profile? (y/n): ").strip().lower()
    if choice == "y":
        user_profile = profile.create_profile_interactively(existing=user_profile)
        profile.save_profile(profile_path, user_profile)
        print("Profile updated.\n")
    else:
        print()

    return user_profile


def show_history(workouts):
    if not workouts:
        print("\nNo workouts logged yet.\n")
        return

    print("\nWorkout history:")
    for w in sorted(workouts, key=lambda w: w["date"]):
        weight_text = f"{w['weight_kg']:g} kg" if w["weight_kg"] is not None else "bodyweight"
        print(f"- {w['date']} | {w['exercise']}: {weight_text}, {w['reps']} reps x {w['sets']} sets")
    print()


def show_comparison(workouts):
    exercises = _available_exercises(workouts)
    if len(exercises) < 2:
        print("\nNot enough data yet - log workouts for at least two different exercises to compare.\n")
        return

    print("\nAvailable exercises:", ", ".join(exercises))
    exercise_a = input("First exercise: ").strip().title()
    exercise_b = input("Second exercise: ").strip().title()

    result = summary.compare_exercises(workouts, exercise_a, exercise_b)

    print()
    for exercise in (exercise_a, exercise_b):
        stats = result[exercise]
        if stats is None:
            print(f"{exercise}: no data logged yet.")
            continue

        status_text = "not enough data" if stats["status"] == "NOT ENOUGH DATA" else stats["status"].title()
        print(f"{exercise}: {stats['sessions']} session(s), trend {status_text} ({stats['change_percent']}%)")
        if stats["best_weight"] is not None:
            print(f"  best weight: {stats['best_weight']:g} kg")
        print(f"  best reps: {stats['best_reps']}")
    print()


def show_summary(workouts):
    stats = summary.build_summary(workouts)
    print("\nProgress summary:")
    print(f"Workouts: {stats['workouts']}")
    print(f"Exercises tracked: {stats['exercises_tracked']}")
    print(f"Personal bests: {stats['personal_bests']}")
    print(f"Plateaus detected: {stats['plateaus_detected']}")
    print(f"Regressions detected: {stats['regressions_detected']}")
    print()


def show_export(workouts, export_dir):
    export_path = export.export_workouts(workouts, export_dir)
    if export_path is None:
        print("\nNo data to export yet - log a workout first.\n")
    else:
        print(f"\nExported {len(workouts)} workout(s) to '{export_path}'.\n")


def _format_month(month_key):
    """Turn '2026-04' into 'Apr 2026'."""
    from datetime import datetime
    return datetime.strptime(month_key, "%Y-%m").strftime("%b %Y")
