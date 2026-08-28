"""
==================== profile.py ====================

This module manages the user's profile: creating one the first
time the program runs, loading it on every following run, and
saving updates. The profile is stored as a small JSON file so it
persists between sessions.

It does not perform any workout analysis - it only knows about the
person using the program, not their training data.
"""

import json
import os
from datetime import date


def load_profile(profile_path):
    """Return the saved profile dict, or None if none exists yet."""
    if not os.path.exists(profile_path):
        return None
    with open(profile_path, encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile_path, profile):
    """Save the profile dict to disk as JSON."""
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def create_profile_interactively(existing=None):
    """Ask the user a few questions and build a profile dict.

    Every field except name is optional - press Enter to skip (or
    to keep the current value, if updating an existing profile).
    """
    existing = existing or {}
    print("\nLet's set up your profile (press Enter to skip a field).")

    name = input(f"Name [{existing.get('name', '')}]: ").strip() or existing.get("name") or "Athlete"
    age = input(f"Age [{existing.get('age', '')}]: ").strip() or existing.get("age")
    sex = input(f"Sex [{existing.get('sex', '')}]: ").strip() or existing.get("sex")
    goal = input(f"Main training goal [{existing.get('goal', '')}]: ").strip() or existing.get("goal")

    return {
        "name": name,
        "age": age,
        "sex": sex,
        "goal": goal,
        "created_on": existing.get("created_on", date.today().isoformat()),
    }
