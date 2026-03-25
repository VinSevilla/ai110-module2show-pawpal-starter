import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Pet, Task, Schedule


# ---------------------------------------------------------------------------
# Test 1 — Task Completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should change a task's status from 'pending' to 'complete'."""
    task = Task(task_name="Morning Walk", duration=30, priority=5, pet_id=1)

    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "complete"


# ---------------------------------------------------------------------------
# Test 2 — Task Addition to a Pet
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Adding tasks to a pet should increase its task_count accordingly."""
    pet = Pet(id=1, name="Buddy", type="Dog", age=3)

    assert pet.task_count == 0

    pet.add_task(Task(task_name="Morning Walk",  duration=30, priority=5, pet_id=pet.id))
    assert pet.task_count == 1

    pet.add_task(Task(task_name="Evening Walk",  duration=30, priority=4, pet_id=pet.id))
    assert pet.task_count == 2


# ---------------------------------------------------------------------------
# Test 3 — Sorting Correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return placed tasks ordered from earliest to latest start minute."""
    schedule = Schedule()

    # Force-place tasks out of chronological order
    task_late  = Task(task_name="Evening Feed", duration=30, priority=3, pet_id=1)
    task_early = Task(task_name="Morning Walk", duration=30, priority=3, pet_id=1)
    task_mid   = Task(task_name="Noon Groom",   duration=30, priority=3, pet_id=1)

    schedule.add_task_at(task_late,  "8:00pm")
    schedule.add_task_at(task_early, "7:00am")
    schedule.add_task_at(task_mid,   "12:00pm")

    ordered = schedule.sort_by_time()
    start_minutes = [start for start, _ in ordered]

    assert start_minutes == sorted(start_minutes), (
        "sort_by_time() did not return tasks in ascending time order"
    )
    # Confirm the first task is the earliest one placed
    assert ordered[0][1].task_name == "Morning Walk"


# ---------------------------------------------------------------------------
# Test 4 — Recurrence Logic
# ---------------------------------------------------------------------------

def test_mark_complete_daily_task_creates_next_day_task():
    """Completing a daily task should return a new Task due the following day."""
    today = date.today()
    task = Task(
        task_name="Morning Walk",
        duration=30,
        priority=5,
        pet_id=1,
        frequency="daily",
        due_date=today,
    )

    next_task = task.mark_complete()

    assert task.status == "complete"
    assert next_task is not None, "Expected a follow-up task for a daily recurring task"
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.task_name == task.task_name


def test_mark_complete_once_task_returns_none():
    """Completing a 'once' task should return None — no follow-up task is created."""
    task = Task(task_name="Vet Visit", duration=60, priority=5, pet_id=1, frequency="once")

    next_task = task.mark_complete()

    assert task.status == "complete"
    assert next_task is None


# ---------------------------------------------------------------------------
# Test 5 — Conflict Detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    """Tasks with overlapping time windows should be flagged by detect_conflicts()."""
    schedule = Schedule()

    task_a = Task(task_name="Walk",  duration=30, priority=5, pet_id=1)  # 9:00–9:30
    task_b = Task(task_name="Groom", duration=30, priority=4, pet_id=1)  # 9:15–9:45 (overlaps)

    # Note: add_task_at keys by start_min — use different start times that genuinely overlap
    schedule.add_task_at(task_a, "9:00am")   # starts at minute 540
    schedule.add_task_at(task_b, "9:15am")   # starts at minute 555, still inside Walk's window

    warnings = schedule.detect_conflicts()

    assert len(warnings) > 0, "Expected at least one conflict warning for overlapping tasks"
    assert any("Walk" in w and "Groom" in w for w in warnings)


def test_detect_conflicts_no_warning_for_sequential_tasks():
    """Back-to-back tasks (end of one == start of next) should not be flagged as conflicts."""
    schedule = Schedule()

    task_a = Task(task_name="Walk",  duration=30, priority=5, pet_id=1)
    task_b = Task(task_name="Groom", duration=30, priority=4, pet_id=1)

    schedule.add_task_at(task_a, "9:00am")   # 9:00–9:30
    schedule.add_task_at(task_b, "9:30am")   # 9:30–10:00 — adjacent, not overlapping

    warnings = schedule.detect_conflicts()

    assert warnings == [], f"Unexpected conflict warnings for sequential tasks: {warnings}"
