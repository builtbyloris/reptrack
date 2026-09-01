# locked-in

A command-line workout tracker that turns a personal training log into clear progress insights: trends, personal bests, plateaus and regressions.

## Why this project

A workout log is easy to collect but harder to interpret. `locked-in` answers a practical question:

> **Am I actually getting better?**

The app starts with an empty workout log and derives every result from the data the user records. No demo data is loaded automatically and no analysis is hardcoded.

## Core workflow

```text
Log workout
    ↓
data/workout_log.csv
    ↓
clean + validate
    ↓
progression / records / summary
    ↓
progress insights
```

The CLI is organized around four user intentions:

```text
LOCKED-IN
├── Log workout
├── View progress
│   ├── Progress summary
│   ├── Exercise progression
│   ├── Personal bests
│   ├── Plateaus
│   ├── Regressions
│   └── Compare exercises
├── Workout history
└── Profile & data
    ├── View / update profile
    └── Export workout data
```

## Features

- Log workouts directly from the CLI
- Track weighted and bodyweight exercises
- View monthly progression for a single exercise
- Classify recent performance as `Progressing`, `Plateau` or `Regressing`
- Track personal bests for weight and reps
- Detect a new personal record immediately after logging a workout
- Review complete workout history
- Compare two exercises side by side
- View an overall progress summary
- Export the current workout log to a timestamped CSV backup
- Create and update a local user profile
- Handle empty, missing or partially invalid data without crashing

## Tech stack

- Python 3.10+
- Python standard library only
- CSV for workout persistence
- JSON for profile persistence

No external dependencies are required.

## Project structure

```text
locked-in/
├── data/
│   ├── workout_log.csv         # generated locally on first run; ignored by git
│   ├── profile.json            # generated locally; ignored by git
│   └── exports/                # generated on demand; ignored by git
├── src/
│   └── locked_in/
│       ├── loader.py           # load, clean and validate workout data
│       ├── entry.py            # add new workouts
│       ├── progression.py      # monthly averages and trend detection
│       ├── records.py          # personal bests and record detection
│       ├── summary.py          # overview and exercise comparison
│       ├── export.py           # CSV export
│       ├── profile.py          # profile persistence
│       └── menu.py             # CLI navigation and output formatting
├── main.py                     # application entry point
├── requirements.txt
└── README.md
```

## How the analysis works

### Data cleaning

`loader.py` validates every CSV row before it reaches the analysis layer.

| Data issue | Example | Handling |
|---|---|---|
| Alternative date format | `11/05/2026` | Accepts `YYYY-MM-DD` and `DD/MM/YYYY` |
| Invalid reps or sets | `eight` | Skips the row and reports it |
| Inconsistent exercise names | ` deadlift ` | Strips whitespace and title-cases the name |
| Missing weight on a weighted exercise | blank Bench Press weight | Skips the row |
| Bodyweight exercise | Pull-up with blank weight | Uses reps as the progression metric |
| Exact duplicate | same session twice | Keeps one entry |
| Missing workout log | fresh installation | Creates an empty CSV with the required headers |

The app does not silently invent or replace workout values.

### Progression detection

Sessions are grouped by calendar month. The main progression metric is:

- `weight_kg` for weighted exercises
- `reps` for bodyweight exercises

Recent monthly averages are compared with the preceding period:

- **Progressing:** change greater than `+3%`
- **Plateau:** change between `-3%` and `+3%`
- **Regressing:** change below `-3%`
- **Not enough data:** fewer than two months available

The model is intentionally simple and transparent. It is designed as a practical training indicator, not as a scientific performance model.

### Personal records

For each exercise, `records.py` tracks:

- highest weight logged
- highest rep count logged
- the date each record occurred

When a new workout is entered, it is compared with that exercise's previous sessions before being saved. If it sets a new record, the CLI reports it immediately.

## Empty-state behavior

A fresh clone is a valid application state. With no workouts recorded, the program reports zero results or explains that more data is needed instead of failing.

```text
Progress summary:
Workouts: 0
Exercises tracked: 0
Personal bests: 0
Plateaus detected: 0
Regressions detected: 0
```

## Installation

```bash
git clone https://github.com/codeloris/locked-in.git
cd locked-in
```

No package installation is needed because the project uses only the standard library.

## Run

```bash
python main.py
```

On the first run, the app creates `data/workout_log.csv` automatically and sets up a small local profile. Both `data/workout_log.csv` and `data/profile.json` are local runtime files and are excluded from version control.

## Example navigation

```text
========================================
              LOCKED-IN
        Workout Progress Tracker
========================================
1. Log workout
2. View progress
3. Workout history
4. Profile & data
0. Exit
```

The main menu contains only the top-level actions. Analysis views are grouped under `View progress`, while profile and export actions are grouped under `Profile & data`.

## Design decisions

The project keeps one source of truth for workout data. `main.py` loads the CSV once into memory, and every feature reads from the same workout list. A newly logged workout is appended both to that list and to the CSV, so the rest of the session immediately sees the updated data.

The modules are separated by responsibility: loading, data entry, analysis, records, summaries, export, profile management and CLI navigation. This keeps the calculation logic independent from the user interface and makes the code easier to extend or test without mixing concerns.

## What I learned

This project reinforced three practical software-design ideas: treating an empty dataset as a normal state, keeping a single source of truth, and separating analysis logic from interface logic. The final CLI also groups related actions by user intent instead of exposing every function as an equal top-level menu choice.

## License

This project is for personal and portfolio use.
