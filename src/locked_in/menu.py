"""
==================== menu.py ====================

Command-line interface for locked-in.

This module owns navigation and output formatting only. Analysis,
storage and profile logic remain in their dedicated modules. The
navigation is grouped by user intent so the main menu stays focused
on the actions used most often.
"""

from locked_in import entry, export, profile, progression, records, summary

MAIN_MENU_TEXT = """
========================================
              LOCKED-IN
        Workout Progress Tracker
========================================
1. Log workout
2. View progress
3. Workout history
4. Profile & data
0. Exit
"""

PROGRESS_MENU_TEXT = """
========================================
            YOUR PROGRESS
========================================
1. Progress summary
2. Exercise progression
3. Personal bests
4. Plateaus
5. Regressions
6. Compare exercises
0. Back
"""

PROFILE_DATA_MENU_TEXT = """
========================================
           PROFILE & DATA
========================================
1. View / update profile
2. Export workout data
0. Back
"""


def run(workouts, csv_path, user_profile, profile_path, export_dir):
    """Start the interactive CLI loop."""
    print(f"Loaded {len(workouts)} workout entries.")

    while True:
        print(MAIN_MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "1":
            entry.add_workout(workouts, csv_path)
        elif choice == "2":
            _run_progress_menu(workouts)
        elif choice == "3":
            show_history(workouts)
        elif choice == "4":
            user_profile = _run_profile_data_menu(
                workouts,
                user_profile,
                profile_path,
                export_dir,
            )
        elif choice == "0":
            print("See you at the next session.")
            break
        else:
            _print_invalid_option()


def _run_progress_menu(workouts):
    """Show analysis-related views under one focused submenu."""
    while True:
        print(PROGRESS_MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "1":
            show_summary(workouts)
        elif choice == "2":
            show_progression(workouts)
        elif choice == "3":
            show_personal_bests(workouts)
        elif choice == "4":
            show_by_status(workouts, "PLATEAU")
        elif choice == "5":
            show_by_status(workouts, "REGRESSING")
        elif choice == "6":
            show_comparison(workouts)
        elif choice == "0":
            return
        else:
            _print_invalid_option()


def _run_profile_data_menu(workouts, user_profile, profile_path, export_dir):
    """Group personal settings and data-management actions."""
    while True:
        print(PROFILE_DATA_MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "1":
            user_profile = show_profile(user_profile, profile_path)
        elif choice == "2":
            show_export(workouts, export_dir)
        elif choice == "0":
            return user_profile
        else:
            _print_invalid_option()


def _available_exercises(workouts):
    return sorted({w["exercise"] for w in workouts})


def _print_invalid_option():
    print("Invalid option, please choose one of the numbers shown.\n")


def show_progression(workouts):
    exercises = _available_exercises(workouts)
    if not exercises:
        print("\nNo workouts logged yet. Log your first workout from the main menu.\n")
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
    for average in averages:
        print(f"{_format_month(average['month'])}: avg {average['average']:.1f} {unit}")

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
        return

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
    analyzable_exercises = 0
    for exercise in exercises:
        sessions = progression.get_exercise_sessions(workouts, exercise)
        averages, _ = progression.monthly_averages(sessions)
        status, change_percent = progression.classify_trend(averages)
        if status == "NOT ENOUGH DATA":
            continue

        analyzable_exercises += 1
        if status == target_status:
            matches.append((exercise, change_percent))

    if analyzable_exercises == 0:
        print(f"\nNot enough monthly data yet to check for {label}.\n")
        return

    print(f"\nExercises with detected {label}:")
    if not matches:
        print("None found.")
    for exercise, change_percent in matches:
        print(f"- {exercise} ({change_percent}%)")
    print()


def show_profile(user_profile, profile_path):
    """Display the current profile and offer to update it."""
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
    for workout in sorted(workouts, key=lambda item: item["date"]):
        weight_text = (
            f"{workout['weight_kg']:g} kg"
            if workout["weight_kg"] is not None
            else "bodyweight"
        )
        print(
            f"- {workout['date']} | {workout['exercise']}: "
            f"{weight_text}, {workout['reps']} reps x {workout['sets']} sets"
        )
    print()


def show_comparison(workouts):
    exercises = _available_exercises(workouts)
    if len(exercises) < 2:
        print(
            "\nNot enough data yet - log workouts for at least two "
            "different exercises to compare.\n"
        )
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

        if stats["status"] == "NOT ENOUGH DATA":
            print(
                f"{exercise}: {stats['sessions']} session(s), "
                "trend not enough data"
            )
        else:
            print(
                f"{exercise}: {stats['sessions']} session(s), "
                f"trend {stats['status'].title()} ({stats['change_percent']}%)"
            )
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
