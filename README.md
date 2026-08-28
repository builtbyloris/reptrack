# locked-in

A command-line workout tracker for logging your own training data and understanding whether you're actually progressing — inspired by the progress charts found in fitness tracking apps.

## Purpose

A workout log of dates, exercises, weights and reps is just a table of numbers. locked-in turns it into an answer to one question: **"Am I actually getting better?"**

## Problem

Raw workout logs are rarely clean, and even when they are, it's hard to tell from a list of sessions whether an exercise is genuinely improving, stuck at a plateau, or quietly regressing. Most tracker demos also ship pre-populated with sample data, which hides how the app actually behaves for a brand-new user with nothing logged yet.

## Solution

locked-in starts completely empty. Every workout, personal best, trend and plateau/regression flag comes exclusively from what the user logs through the CLI. All ten menu options read from the same in-memory list of workouts — there's a single source of truth, not a separate dataset per feature.

```
User input (option 5)
        ↓
data/workout_log.csv   (single source of truth, on disk and in memory)
        ↓
progression.py / records.py / summary.py / export.py
        ↓
options 1-4, 7-10 (all read-only views over the same data)
```

## Features

- Starts genuinely empty: zero workouts, zero personal bests, zero trends, until the user logs something
- Log new workouts directly from the CLI (option 5), appended to the CSV log
- View month-by-month progression for any exercise, with automatic Progressing / Plateau / Regressing classification
- Personal bests (max weight, max reps) per exercise, updated live as soon as a new workout is logged
- New personal record detection with short motivational feedback
- Full workout history, sortable list of everything logged
- Side-by-side comparison between two exercises
- Overall progress summary (workout count, exercises tracked, personal bests, plateaus, regressions)
- Export the current log to a timestamped CSV backup
- A simple user profile (name, age, sex, training goal) created on first run and reused on future sessions
- Graceful empty-state and error handling everywhere — no crashes on missing data

## Technologies

- Python 3.10+
- Standard library only (`csv`, `json`, `datetime`, `collections`) — no external dependencies

## Project Structure

```
locked-in/
├── data/
│   ├── workout_log.csv         # the user's real data - starts empty (header only)
│   ├── sample_workout_log.csv  # optional demo dataset, not loaded automatically
│   ├── profile.json            # created on first run, not tracked in git
│   └── exports/                # created on demand by option 10, not tracked in git
├── src/
│   └── locked_in/
│       ├── loader.py        # reading, cleaning and validating the CSV data
│       ├── progression.py   # monthly averages + trend classification
│       ├── records.py       # personal bests + new-record detection
│       ├── entry.py         # logging a new workout from the CLI
│       ├── summary.py       # progress summary + exercise comparison
│       ├── export.py        # exporting the current log to a CSV backup
│       ├── profile.py       # user profile creation and persistence
│       └── menu.py          # CLI menu - routes choices, no calculations
├── main.py                  # entry point
├── README.md
├── requirements.txt
└── .gitignore
```

## How It Works

1. `main.py` loads `data/workout_log.csv` through `loader.py`. On a fresh install this file only has a header row, so the app starts with zero workouts - that's a normal state, not an error, and nothing is hardcoded to hide it.
2. Every row is validated and normalized; rows that can't be repaired are skipped and reported at startup instead of crashing the program.
3. On first run, `profile.py` interactively creates a small profile and saves it to `data/profile.json`; on later runs it's loaded automatically and the user is greeted by name.
4. `menu.py` presents an interactive CLI. Every option reads from the same in-memory `workouts` list - logging a workout (option 5) appends to that list and to the CSV file, and every other option (1-4, 7-10) recalculates its answer from that same list on demand. There's no caching and no separate per-feature dataset, so a newly logged workout is reflected everywhere immediately.

## Empty State

With nothing logged yet, every menu option responds with an explicit, honest message instead of a blank screen or a crash:

```
Workouts: 0
Exercises tracked: 0
Personal bests: 0
Plateaus detected: 0
Regressions detected: 0
```

- Progression / personal bests / history → "no data yet, log a workout first"
- Plateau / regression checks / comparison → "not enough data yet"
- Export → "no data to export yet"

As soon as the user logs a workout, all of these switch over automatically - there's no separate "demo mode" to turn off.

## Data Cleaning

`loader.py` handles a few real-world imperfections found in the optional sample dataset (`data/sample_workout_log.csv`), and the same rules apply to anything logged manually:

| Issue | Example | Handling |
|---|---|---|
| Non-standard date format | `11/05/2026` instead of `2026-05-11` | Both `YYYY-MM-DD` and `DD/MM/YYYY` are parsed |
| Non-numeric reps | `"eight"` | Row is skipped and reported |
| Inconsistent exercise naming | `" deadlift "` vs `"Deadlift"` | Names are stripped and title-cased |
| Missing weight on a weighted exercise | blank `weight_kg` for an Overhead Press session | Treated as a missing value and skipped — **not** confused with a genuine bodyweight exercise |
| Genuine bodyweight exercise | Pull-up always has blank `weight_kg` | Recognized as bodyweight (an exercise that *never* has a weight logged anywhere in the file) and analyzed by reps instead |
| Duplicate entry | the same session logged twice | Exact duplicates are removed |
| Missing/empty log file | fresh install, no `workout_log.csv` yet | A new file with just the header row is created automatically |

Cleaning never silently rewrites a value — a row is either kept as-is or skipped and reported, so the dataset's meaning isn't altered.

## Progression Detection Logic

For each exercise, sessions are grouped by calendar month and averaged (weight for barbell/dumbbell exercises, reps for bodyweight ones). The trend is classified by comparing the most recent one or two months against the one or two months right before them — not the whole history — so a plateau or dip in the last few weeks isn't hidden by earlier progress:

- **Progressing** — recent average is more than 3% above the previous window
- **Plateau** — change is within ±3%
- **Regressing** — recent average is more than 3% below the previous window

With fewer than two months of data, the status is reported as "not enough data" instead of forcing a guess.

## Personal Records

`records.py` tracks the best weight and best rep count ever logged per exercise, and replays each exercise's history to flag exactly when a new record was set. If the *most recent* session set a record, the CLI shows a `NEW PERSONAL RECORD!` message with a short motivational line.

The same detection logic runs live: when a new workout is logged (option 5), `entry.py` compares it against that exercise's previous best weight and best reps *before* saving it, and shows the same confirmation and motivational message immediately if it's a new record.

## Comparing Exercises and Progress Summary

`summary.py` builds two cross-exercise views on top of the same `progression.py` and `records.py` functions used everywhere else:

- **Compare exercises** (option 8) — session count, current trend and personal bests for two exercises side by side. Requires data for at least two different exercises.
- **Progress summary** (option 9) — overall counts: total workouts, exercises tracked, personal bests, and how many exercises are currently flagged as a plateau or a regression.

## Exporting Data

Option 10 writes every currently logged workout to a new timestamped CSV file under `data/exports/`, useful as a manual backup. With nothing logged yet, it reports that there's nothing to export instead of creating an empty file.

## User Profile

On first run, `profile.py` asks for a name, age, sex and training goal (all except name are optional) and saves them to `data/profile.json`. On every later run the profile is loaded automatically and the user is greeted by name; option 6 lets them view or update it at any time. The profile file is excluded from version control via `.gitignore`, since it holds personal data rather than sample/portfolio data.

## Installation

```bash
git clone https://github.com/codeloris/locked-in.git
cd locked-in
```

No dependencies to install — standard library only.

## How to Run

```bash
python main.py
```

The app starts empty. To explore it with realistic data instead of logging everything by hand, copy the included demo dataset over the live log before running:

```bash
cp data/sample_workout_log.csv data/workout_log.csv
python main.py
```

## Example CLI Output

Logging a first workout and immediately seeing it reflected everywhere:

```
Select an option: 5
Exercise: Bench Press
Weight in kg (leave blank if bodyweight): 60
Reps: 8
Sets: 3
Date (YYYY-MM-DD, leave blank for today): 2026-08-28

Workout saved.

Select an option: 9

Progress summary:
Workouts: 1
Exercises tracked: 1
Personal bests: 1
Plateaus detected: 0
Regressions detected: 0
```

## Future Improvements

- Estimated one-rep max (1RM) using a standard formula
- A simple text-based trend chart per exercise
- A "most improved exercise" summary across the whole log
- Support for multiple separate profiles/logs in the same install
- Scheduled/automatic exports instead of manual only
- Unit tests for the progression-detection and record logic

## What I Learned

The biggest architectural lesson here wasn't the trend math - it was resisting the temptation to ship a pre-populated demo as the default state. Making "zero workouts" a fully supported, explicitly handled state (rather than an edge case bolted on later) forced every module to read from one real source of truth instead of assuming data would always be there. Keeping the demo dataset available but opt-in, instead of auto-loaded, was a small decision that made the whole app honestly reflect what the user has actually logged.

## License

This project is for personal/portfolio use.
