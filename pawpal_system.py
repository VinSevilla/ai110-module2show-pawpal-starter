from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


# ---------------------------------------------------------------------------
# Dataclasses — simple data-holding objects (Pet and Task)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    id: int
    name: str
    type: str
    age: int
    # Calculated automatically from scheduled tasks — not set by the user
    #change5: maintenance level is now calculated based on the pet's scheduled tasks, so it is initialized to a default value of 1 and
    #updated by the update_maintenance_level method after schedule generation.
    maintenance_level: int = field(init=False, default=1)
    tasks: List["Task"] = field(init=False, default_factory=list)

    @property
    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)

    def add_task(self, task: "Task"):
        """Assign a task directly to this pet."""
        self.tasks.append(task)

    def edit_pet_info(self, name: str = None, type: str = None, age: int = None):
        """Update one or more fields on this pet."""
        if name is not None:
            self.name = name
        if type is not None:
            self.type = type
        if age is not None:
            self.age = age

    FEED_KEYWORDS = {"feed", "eat", "meal", "food", "breakfast", "lunch", "dinner"}

    def update_maintenance_level(self, tasks: List["Task"]):
        """Score care quality 1–5: 2 walks + 2 meals = 4/5, grooming adds the 5th point."""
        walks  = sum(1 for t in tasks if "walk" in t.task_name.lower())
        feeds  = sum(
            1 for t in tasks
            if any(kw in t.task_name.lower() for kw in self.FEED_KEYWORDS)
        )
        grooms = sum(1 for t in tasks if "groom" in t.task_name.lower())

        # 2 walks + 2 meals = 4/5; grooming pushes to 5/5
        completed = min(walks, 2) + min(feeds, 2)  # 0–4
        score = max(1, completed)

        if grooms >= 1:
            score = min(5, score + 1)

        self.maintenance_level = score

    def view_pet_info(self) -> str:
        """Return a formatted string of this pet's details."""
        return (
            f"[Pet #{self.id}] {self.name} | Type: {self.type} | "
            f"Age: {self.age} | Maintenance Level: {self.maintenance_level}/5"
        )


@dataclass
#Changes1: removed id attribute from Task class since it was not necessary and slightly
# overcomplicated the system.
class Task:
    task_name: str
    duration: int   # in minutes
    priority: int   # 1 (low) to 5 (high)
    pet_id: int     # which pet this task belongs to
    status: str = field(init=False, default="pending")  # "pending" or "complete"
    recurring: bool = False           # True = repeat this task throughout the day
    repeat_every: int = 0             # minutes between each recurrence (0 = not recurring)
    frequency: str = "once"           # "once", "daily", or "weekly"
    due_date: Optional[date] = None   # date this task is due; defaults to today if not set

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete; returns a new Task for the next occurrence if daily/weekly."""
        self.status = "complete"
        base_date = self.due_date or date.today()

        if self.frequency == "daily":
            next_date = base_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = base_date + timedelta(weeks=1)
        else:
            return None  # "once" tasks don't recur

        return Task(
            task_name=self.task_name,
            duration=self.duration,
            priority=self.priority,
            pet_id=self.pet_id,
            frequency=self.frequency,
            due_date=next_date,
        )

    def edit_duration(self, duration: int):
        """Update how long this task takes (in minutes)."""
        self.duration = duration

    def edit_priority(self, priority: int):
        """Update the priority level of this task."""
        self.priority = priority




# ---------------------------------------------------------------------------
# Schedule — manages tasks within a 24-hour (12am–12am) daily block
# ---------------------------------------------------------------------------

class Schedule:

    MINUTES_IN_DAY = 1440  # 24 hours × 60 minutes
    MIN_GAP = 120          # minimum minutes between two instances of the same task on the same pet

    # Keyword → preferred (start, end) window in minutes from midnight
    KEYWORD_WINDOWS = {
        "breakfast": (60,   720),   # 1 AM – 12 PM
        "morning":   (60,   720),
        "lunch":     (720,  1080),  # 12 PM – 6 PM
        "afternoon": (720,  1080),
        "dinner":    (1080, 1440),  # 6 PM – 12 AM
        "evening":   (1080, 1440),
    }

    def __init__(self, day_start: int = 0, day_end: int = 1440):
        """Initialize an empty schedule bounded by day_start and day_end (minutes from midnight)."""
        self.day_start: int = day_start
        self.day_end: int = day_end
        # Each entry is a (start_minute, end_minute) pair representing a blocked range
        self.blocked_times: List[tuple] = []
        self.blocked_labels: List[str] = []
        self.tasks: List[Task] = []
        # Filled by generate_schedule(): maps start_minute -> Task
        self._placed: dict = {}
        # Tasks that couldn't fit anywhere after generate_schedule()
        self._unplaced: List[Task] = []

    @staticmethod
    def _parse_time(time_str: str) -> int:
        """Parse a 12-hour time string (e.g. '5pm', '8:30am') into minutes from midnight."""
        import re
        time_str = time_str.strip().lower().replace(" ", "")
        match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)", time_str)
        if not match:
            raise ValueError(
                f"Unrecognized time format: '{time_str}'. "
                "Use formats like '5pm', '5:30pm', or '12:00am'."
            )
        hours   = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        period  = match.group(3)

        if hours < 1 or hours > 12 or minutes > 59:
            raise ValueError(f"Invalid time value: '{time_str}'.")

        # Convert to 24-hour then to minutes from midnight
        if period == "am":
            hours = 0 if hours == 12 else hours        # 12am -> 0
        else:
            hours = 12 if hours == 12 else hours + 12  # 12pm -> 12, 1pm -> 13

        return hours * 60 + minutes

    def add_task(self, task: Task):
        """Add a care task to the unscheduled pool."""
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        """Remove a task from both the pool and the placed schedule."""
        self.tasks = [t for t in self.tasks if t.task_name != task_name]
        self._placed = {k: v for k, v in self._placed.items()
                        if v.task_name != task_name}

    def block_time(self, start: int, end: int, label: str = ""):
        """Mark a time range (in minutes from midnight) as unavailable for scheduling."""
        self.blocked_times.append((start, end))
        self.blocked_labels.append(label)

    def _preferred_window(self, task: Task):
        """Return (start, end) minutes for a task based on name keywords, or None if no match."""
        name = task.task_name.lower()
        for keyword, window in self.KEYWORD_WINDOWS.items():
            if keyword in name:
                return window
        return None

    def _respects_gap(self, task: Task, start: int) -> bool:
        """Return True if placing task at start keeps at least MIN_GAP from any same-name/same-pet task."""
        for placed_start, placed_task in self._placed.items():
            if placed_task.task_name == task.task_name and placed_task.pet_id == task.pet_id:
                if abs(start - placed_start) < self.MIN_GAP:
                    return False
        return True

    def _slot_is_free(self, start: int, duration: int) -> bool:
        """Return True if [start, start+duration) fits inside the day with no conflicts."""
        end = start + duration
        if end > self.day_end:
            return False
        for b_start, b_end in self.blocked_times:
            if not (end <= b_start or start >= b_end):
                return False
        for placed_start, placed_task in self._placed.items():
            placed_end = placed_start + placed_task.duration
            if not (end <= placed_start or start >= placed_end):
                return False
        return True

    def _expand_recurring(self) -> List[Task]:
        """Expand recurring tasks into repeated copies spaced by repeat_every minutes."""
        expanded = []
        for task in self.tasks:
            expanded.append(task)
            if task.recurring and task.repeat_every > 0:
                offset = task.repeat_every
                while offset + task.duration <= self.MINUTES_IN_DAY:
                    copy = Task(
                        task_name=task.task_name,
                        duration=task.duration,
                        priority=task.priority,
                        pet_id=task.pet_id,
                    )
                    expanded.append(copy)
                    offset += task.repeat_every
        return expanded

    def generate_schedule(self) -> dict:
        """Place tasks by priority, respecting keyword time windows and per-pet spacing."""
        self._placed = {}
        self._unplaced = []
        for task in sorted(self._expand_recurring(), key=lambda t: t.priority, reverse=True):
            placed = False

            # Build search order: preferred window first, then full day as fallback
            preferred = self._preferred_window(task)
            search_ranges = []
            if preferred:
                pref_start = max(preferred[0], self.day_start)
                pref_end   = min(preferred[1], self.day_end)
                if pref_start < pref_end:
                    search_ranges.append(range(pref_start, pref_end, 15))
            search_ranges.append(range(self.day_start, self.day_end, 15))

            # Pass 1: honor both the keyword window and the spacing gap
            for search_range in search_ranges:
                for minute in search_range:
                    if self._slot_is_free(minute, task.duration) and self._respects_gap(task, minute):
                        self._placed[minute] = task
                        placed = True
                        break
                if placed:
                    break

            # Pass 2: relax the gap constraint (tasks too close together is better than unplaced)
            if not placed:
                for minute in range(self.day_start, self.day_end, 15):
                    if self._slot_is_free(minute, task.duration):
                        self._placed[minute] = task
                        placed = True
                        break

            if not placed:
                self._unplaced.append(task)
        return dict(sorted(self._placed.items()))

    def add_task_at(self, task: Task, time_str: str):
        """Force-place a task at a specific time without conflict checking (use detect_conflicts after)."""
        start_min = self._parse_time(time_str)
        self.tasks.append(task)
        self._placed[start_min] = task

    def detect_conflicts(self) -> List[str]:
        """Scan placed tasks for overlapping time slots; return warning strings (empty = no conflicts)."""
        warnings = []
        items = sorted(self._placed.items())   # [(start_min, task), ...]

        for i in range(len(items)):
            a_start, task_a = items[i]
            a_end = a_start + task_a.duration

            for j in range(i + 1, len(items)):
                b_start, task_b = items[j]
                b_end = b_start + task_b.duration

                # Two ranges overlap when one starts before the other ends
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"WARNING: '{task_a.task_name}' "
                        f"({self._to_time(a_start)}–{self._to_time(a_end)}) "
                        f"overlaps with '{task_b.task_name}' "
                        f"({self._to_time(b_start)}–{self._to_time(b_end)})"
                    )

        return warnings

    def sort_by_time(self) -> List[tuple]:
        """Return placed tasks as (start_min, task) pairs sorted chronologically using a lambda key."""
        return sorted(
            self._placed.items(),
            key=lambda item: item[0]   # item[0] is start_minute (int); lower = earlier in the day
        )

    def filter_tasks(self, pet_id: int = None, status: str = None) -> List[Task]:
        """Filter placed tasks by pet_id and/or completion status; omit a param to skip that filter."""
        results = list(self._placed.values())
        if pet_id is not None:
            results = [t for t in results if t.pet_id == pet_id]
        if status is not None:
            results = [t for t in results if t.status == status]
        return results

    def complete_task(self, task_name: str) -> Optional[Task]:
        """Mark a placed task complete and auto-add its next occurrence if daily or weekly."""
        for task in self._placed.values():
            if task.task_name == task_name:
                next_task = task.mark_complete()
                if next_task:
                    self.tasks.append(next_task)  # queued for the next generate_schedule()
                return next_task
        return None

    def check_conflicts(self) -> List[Task]:
        """Return tasks that could not be placed after the last generate_schedule() call."""
        return list(self._unplaced)

    def get_tasks_for_pet(self, pet_id: int) -> List[Task]:
        """Return all placed tasks that belong to a given pet."""
        return [t for t in self._placed.values() if t.pet_id == pet_id]

    def view_schedule(self):
        """Print the day's schedule from 12 AM to 12 AM."""
        if not self._placed:
            print("No schedule generated yet — call generate_schedule() first.")
            return
        for start_min, task in sorted(self._placed.items()):
            end_min = start_min + task.duration
            print(f"  {self._to_time(start_min)} – {self._to_time(end_min)}"
                  f"  {task.task_name} ({task.duration} min, priority {task.priority})")

    @staticmethod
    def _to_time(minutes: int) -> str:
        """Convert minutes-from-midnight to a 12-hour clock string (e.g. '8:30 AM')."""
        h, m = divmod(minutes, 60)
        period = "AM" if h < 12 else "PM"
        h = h % 12 or 12  # convert 0 -> 12, 13 -> 1, etc.
        return f"{h}:{m:02d} {period}"


# ---------------------------------------------------------------------------
# User — the pet owner, ties everything together
# ---------------------------------------------------------------------------
#Change4: Added a add_constraint method to the User class, which allows the user to block off time in their schedule for 
#specific plans (e.g. work, gym, dinner). This is important for the schedule generation to take into account the user's availability when scheduling pet care tasks.
class User:
    def __init__(self, id: int, name: str):
        """Initialize a user with a name, an empty schedule, and no pets."""
        self.id: int = id
        self.name: str = name
        self.user_schedule: Schedule = Schedule()
        self.user_pets: List[Pet] = []

    def edit_user_info(self, name: str):
        """Update the user's name."""
        self.name = name

    def view_user_info(self) -> str:
        """Return a formatted string of this user's details."""
        pet_names = [p.name for p in self.user_pets]
        return (
            f"[User #{self.id}] {self.name} | "
            f"Pets: {', '.join(pet_names) if pet_names else 'None'}"
        )

    def add_pet(self, pet: Pet):
        """Register a pet under this user's care."""
        self.user_pets.append(pet)

    def remove_pet(self, pet_id: int):
        """Remove a pet from this user's care by its ID."""
        self.user_pets = [p for p in self.user_pets if p.id != pet_id]

    def filter_tasks_by_pet_name(self, pet_name: str = None, status: str = None) -> List[Task]:
        """Filter placed tasks by pet name (string) and/or status; resolves name to id internally."""
        pet_id = None
        if pet_name is not None:
            match = next((p for p in self.user_pets if p.name.lower() == pet_name.lower()), None)
            if match is None:
                return []
            pet_id = match.id
        return self.user_schedule.filter_tasks(pet_id=pet_id, status=status)

    def update_pet_maintenance(self):
        """Recalculate maintenance_level for all pets based on their placed schedule tasks."""
        for pet in self.user_pets:
            tasks = self.user_schedule.get_tasks_for_pet(pet.id)
            pet.update_maintenance_level(tasks)

    def add_constraint(self, label: str, start_time: str, end_time: str):
        """Block off a named time window (e.g. 'Work', '9am'–'5pm') in the user's schedule."""
        start_min = Schedule._parse_time(start_time)
        end_min   = Schedule._parse_time(end_time)
        if end_min <= start_min:
            raise ValueError(
                f"End time '{end_time}' must be after start time '{start_time}'."
            )
        for i, (b_start, b_end) in enumerate(self.user_schedule.blocked_times):
            if start_min < b_end and end_min > b_start:
                existing_label = self.user_schedule.blocked_labels[i]
                raise ValueError(
                    f"This time block overlaps with existing constraint '{existing_label}' "
                    f"({Schedule._to_time(b_start)}–{Schedule._to_time(b_end)})."
                )
        self.user_schedule.block_time(start_min, end_min, label=label)
        # Invalidate any existing generated schedule so it must be regenerated
        self.user_schedule._placed = {}
        self.user_schedule._unplaced = []
        print(f"Constraint added: '{label}' from {Schedule._to_time(start_min)} "
              f"to {Schedule._to_time(end_min)}")


