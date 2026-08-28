"""
==================== main.py ====================

Entry point for locked-in. Loads the user's workout log (starting
empty on a fresh install), sets up the profile on first run, reports
any rows that had to be cleaned out, and starts the CLI menu.

It does not contain any analysis or cleaning logic itself - it only
coordinates the other modules.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from locked_in import loader, menu, profile

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_PATH = os.path.join(DATA_DIR, "workout_log.csv")
PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")


def main():
    try:
        workouts, skipped = loader.load_workouts(DATA_PATH)
    except ValueError as e:
        print(f"Could not read the workout log: {e}")
        sys.exit(1)

    if skipped:
        print(f"Cleaned {len(skipped)} problematic row(s) out of the dataset:")
        for row, reason in skipped:
            print(f"  - {reason}")
        print()

    user_profile = profile.load_profile(PROFILE_PATH)
    if user_profile is None:
        print("No profile found yet - let's create one.")
        user_profile = profile.create_profile_interactively()
        profile.save_profile(PROFILE_PATH, user_profile)
        print(f"\nProfile saved. Welcome, {user_profile['name']}!\n")
    else:
        print(f"\nWelcome back, {user_profile['name']}!\n")

    menu.run(workouts, DATA_PATH, user_profile, PROFILE_PATH, EXPORT_DIR)


if __name__ == "__main__":
    main()
