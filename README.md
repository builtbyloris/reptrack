# RepTrack

A command-line workout tracker that turns a personal training log into clear progress insights: trends, personal bests, plateaus and regressions.

## Why this project

A workout log is easy to collect but harder to interpret. RepTrack answers a practical question:

> **Am I actually getting better?**

The app starts with an empty workout log and derives every result from the data recorded by the user. No demo data is loaded automatically and no analysis is hardcoded.

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

The CLI is organized around four main user intentions:

```text
REPTRACK
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

* Log workouts directly from the CLI
* Track weighted and bodyweight exercises
* View monthly progression for a single exercise
* Classify recent performance as `Progressing`, `Plateau` or `Regressing`
* Track personal bests for weight and reps
* Detect a new personal record immediately after logging a workout
* Review complete workout history
* Compare two exercises side by side
* View an overall progress summary
* Export the current workout log to a timestamped CSV backup
* Create and update a local user profile
* Handle empty, missing or partially invalid data without crashing

## Tech stack

* Python 3.10+
* Python standard library only
* CSV for workout persistence
* JSON for profile persistence

No external dependencies are required.

## Project structure

```text
reptrack/
├── data/
│   ├── workout_log.csv         # generated locally on first run; ignored by git
│   ├── profile.json            # generated locally; ignored by git
│   └── exports/                # generated on demand; ignored by git
├── src/
│   └── reptrack/
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

| Data issue                            | Example                   | Handling                                       |
| ------------------------------------- | ------------------------- | ---------------------------------------------- |
| Alternative date format               | `11/05/2026`              | Accepts `YYYY-MM-DD` and `DD/MM/YYYY`          |
| Invalid reps or sets                  | `eight`                   | Skips the row and reports it                   |
| Inconsistent exercise names           | `deadlift`                | Strips whitespace and title-cases the name     |
| Missing weight on a weighted exercise | blank Bench Press weight  | Skips the row                                  |
| Bodyweight exercise                   | Pull-up with blank weight | Uses reps as the progression metric            |
| Exact duplicate                       | same session twice        | Keeps one entry                                |
| Missing workout log                   | fresh installation        | Creates an empty CSV with the required headers |

The app does not silently invent or replace workout values.

### Progression detection

Sessions are grouped by calendar month.

The main progression metric is:

* `weight_kg` for weighted exercises
* `reps` for bodyweight exercises

Recent monthly averages are compared with the preceding period:

* **Progressing:** change greater than `+3%`
* **Plateau:** change between `-3%` and `+3%`
* **Regressing:** change below `-3%`
* **Not enough data:** fewer than two months available

The model is intentionally simple and transparent. It is designed as a practical training indicator, not as a scientific performance model.

### Personal records

For each exercise, `records.py` tracks:

* highest weight logged
* highest rep count logged
* the date each record occurred

When a new workout is entered, it is compared with that exercise's previous sessions before being saved.

If it sets a new personal record, the CLI reports it immediately.

## Empty-state behavior

A fresh clone is a valid application state.

With no workouts recorded, the program reports zero results or explains that more data is needed instead of failing.

```text
Progress summary:
Workouts: 0
Exercises tracked: 0
Personal bests: 0
Plateaus detected: 0
Regressions detected: 0
```

## Installation

Clone the repository:

```bash
git clone https://github.com/codeloris/reptrack.git
cd reptrack
```

No package installation is required because the project uses only the Python standard library.

## Run

Start the application with:

```bash
python main.py
```

On the first run, RepTrack creates `data/workout_log.csv` automatically and sets up a local user profile.

Both `data/workout_log.csv` and `data/profile.json` are runtime files and are excluded from version control.

## Example navigation

```text
========================================
               REPTRACK
        Workout Progress Tracker
========================================

1. Log workout
2. View progress
3. Workout history
4. Profile & data

0. Exit
```

The main menu contains only top-level actions.

Analysis views are grouped under `View progress`, while profile and export actions are grouped under `Profile & data`.

This keeps the CLI compact and avoids exposing every feature at the same navigation level.

## Design decisions

### Single source of truth

The project keeps one source of truth for workout data.

`main.py` loads the workout log into memory and every feature reads from the same workout list.

When a new workout is logged, it is appended both to the in-memory list and to the CSV file, so the rest of the current session immediately sees the updated data.

### Separation of responsibilities

The modules are separated by responsibility:

* data loading and validation
* workout entry
* progression analysis
* personal records
* summaries and comparisons
* data export
* profile management
* CLI navigation

This keeps calculation logic separate from interface logic and makes the code easier to understand, maintain and test.

### Local-first design

RepTrack is intentionally lightweight.

It does not require:

* a database
* an external API
* an internet connection
* third-party Python libraries

Workout and profile data remain stored locally on the user's machine.

## What I learned

This project reinforced several practical software-development concepts:

* treating an empty dataset as a normal application state
* validating data before analysis
* maintaining a single source of truth
* separating business logic from interface logic
* organizing modules by responsibility
* designing CLI navigation around user intentions instead of individual functions
* handling persistence without external dependencies
* translating raw workout data into simple, interpretable progress indicators

RepTrack started as a basic workout logger and evolved into a small structured application focused on clean architecture, reliable data handling and understandable progress analysis.

