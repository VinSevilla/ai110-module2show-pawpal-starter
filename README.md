# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Beyond basic task placement, the scheduler includes several improvements that make it more useful for a real pet owner:

- **Sort by time** — `sort_by_time()` returns the placed schedule in chronological order using a lambda key, regardless of the order tasks were added.
- **Filter by pet or status** — `filter_tasks()` and `filter_tasks_by_pet_name()` let you narrow the schedule to one pet or show only pending/completed tasks.
- **Recurring tasks** — set `frequency="daily"` or `frequency="weekly"` on a `Task`. When `complete_task()` is called, it automatically creates the next occurrence with the correct due date using Python's `datetime.timedelta`.
- **Conflict detection** — `detect_conflicts()` scans the placed schedule for overlapping time slots and returns human-readable warning messages without crashing. An early-exit optimization keeps it fast for typical daily schedules.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest
```

For verbose output showing each test name:

```bash
python -m pytest -v
```

### What the tests cover

| Test                                                    | Behavior verified                                                                   |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `test_mark_complete_changes_status`                     | Completing a task flips its status from `pending` to `complete`                     |
| `test_add_task_increases_pet_task_count`                | Adding tasks to a `Pet` increments `task_count` correctly                           |
| `test_sort_by_time_returns_chronological_order`         | `sort_by_time()` returns placed tasks earliest→latest regardless of insertion order |
| `test_mark_complete_daily_task_creates_next_day_task`   | Completing a `daily` task auto-generates a follow-up task due the next day          |
| `test_mark_complete_once_task_returns_none`             | Completing a `once` task returns `None` — no infinite recurrence                    |
| `test_detect_conflicts_flags_overlapping_tasks`         | `detect_conflicts()` catches tasks with overlapping time windows                    |
| `test_detect_conflicts_no_warning_for_sequential_tasks` | Back-to-back tasks (end == next start) are not falsely flagged as conflicts         |

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Features

- **Priority-based task scheduling** — `generate_schedule()` sorts tasks by priority (1–5, highest first) and greedily places each one into the earliest available 15-minute-aligned slot in the 24-hour day.

- **Chronological schedule display** — `sort_by_time()` returns placed tasks sorted by start minute using a lambda key, so the daily view always renders in time order.

- **Conflict detection** — `detect_conflicts()` runs a pairwise scan over all placed tasks and reports any overlapping time windows as human-readable warning strings.

- **Unplaced task tracking** — `check_conflicts()` returns tasks that could not fit into any free slot after scheduling, surfaced as a separate warning in the UI.

- **Owner time-blocking (constraints)** — `add_constraint()` parses natural 12-hour time strings (e.g. `"9:00am"`) via a regex parser and marks those windows as unavailable before scheduling runs.

- **Daily and weekly task recurrence** — `mark_complete()` on a task with `frequency="daily"` or `"weekly"` automatically creates a next-occurrence task with the appropriate due date offset, queued for the next schedule generation.

- **Intra-day recurring task expansion** — Tasks with `recurring=True` and a `repeat_every` interval are expanded into multiple copies spaced throughout the day before scheduling begins.

- **Pet maintenance scoring** — `update_maintenance_level()` scores each pet 1–5 after schedule generation by counting walks (target: 2), feeds (target: 2), and grooming sessions (+1 bonus, capped at 5).

- **Per-pet and per-status task filtering** — `filter_tasks()` and `filter_tasks_by_pet_name()` allow lookup of placed tasks by pet ID/name and completion status (`"pending"` / `"complete"`).

- **12-hour time string parsing** — `_parse_time()` handles formats like `5pm`, `8:30am`, and `12:00pm` with full AM/PM edge-case handling for midnight and noon.

## 📸 Demo

<a href="/course_images/ai110/Screenshot 2026-03-27 at 11.21.25 AM.png" target="_blank"><img src='/course_images/ai110/Screenshot 2026-03-27 at 11.21.25 AM.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
