from dataclasses import dataclass, field
from typing import List


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
    maintenance_level: int = field(init=False, default=1)

    def edit_pet_info(self, name: str = None, type: str = None, age: int = None):
        """Update one or more fields on this pet."""
        if name is not None:
            self.name = name
        if type is not None:
            self.type = type
        if age is not None:
            self.age = age

    def update_maintenance_level(self, tasks: List["Task"]):
        """
        Recalculate maintenance_level based on the pet's scheduled tasks.

        Scoring rules (target: 2 walks + 2 feeds = 4 tasks):
          Base score = total required tasks completed (out of 4), minimum 1.
          Groom/bath adds 1 full bonus point (max 5).
            4 tasks + groom = 5  |  4 tasks = 4
            3 tasks + groom = 4  |  3 tasks = 3
            2 tasks + groom = 3  |  2 tasks = 2
            1 task  + groom = 2  |  0-1 tasks = 1
        """
        walks  = sum(1 for t in tasks if "walk"  in t.task_name.lower())
        feeds  = sum(1 for t in tasks if "feed"  in t.task_name.lower())
        grooms = sum(1 for t in tasks if "groom" in t.task_name.lower())

        # Count only up to the required 2 of each type (total out of 4)
        completed = min(walks, 2) + min(feeds, 2)  # 0–4
        score = max(1, completed)                   # floor of 1

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

    # Change2: For simplicity, made the schedule operate on a single 24-hour block (12 AM to 12 AM)
    # Change3: added a parseable time format for the block_time function, so the user can input time in a more 
    # readable way (e.g. "9:00 AM" instead of 540 minutes).
    MINUTES_IN_DAY = 1440  # 24 hours × 60 minutes

    def __init__(self):
        # Each entry is a (start_minute, end_minute) pair representing a blocked range
        self.blocked_times: List[tuple] = []
        self.tasks: List[Task] = []
        # Filled by generate_schedule(): maps start_minute -> Task
        self._placed: dict = {}

    @staticmethod
    def _parse_time(time_str: str) -> int:
        """
        Convert a user-facing time string to minutes from midnight.

        Accepted formats (case-insensitive, space optional):
            "5pm"  "5:00pm"  "5:30 PM"  "12:00am"  "12:30AM"
        Returns minutes from midnight (0–1439).
        Raises ValueError for unrecognized input.
        """
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

    def block_time(self, start: int, end: int):
        """
        Mark a time range as unavailable (e.g. owner at work).
        start / end are minutes from midnight: 0 = 12:00 AM, 1440 = 12:00 AM next day.
        """
        self.blocked_times.append((start, end))

    def _slot_is_free(self, start: int, duration: int) -> bool:
        """Return True if [start, start+duration) fits inside the day with no conflicts."""
        end = start + duration
        if end > self.MINUTES_IN_DAY:
            return False
        for b_start, b_end in self.blocked_times:
            if not (end <= b_start or start >= b_end):
                return False
        for placed_start, placed_task in self._placed.items():
            placed_end = placed_start + placed_task.duration
            if not (end <= placed_start or start >= placed_end):
                return False
        return True

    def generate_schedule(self) -> dict:
        """
        Fit all tasks into the 24-hour block.
        Tasks are placed in priority order (highest first), earliest available slot,
        checked every 15 minutes.
        Returns an ordered dict of { start_minute: Task }.
        """
        self._placed = {}
        for task in sorted(self.tasks, key=lambda t: t.priority, reverse=True):
            for minute in range(0, self.MINUTES_IN_DAY, 15):
                if self._slot_is_free(minute, task.duration):
                    self._placed[minute] = task
                    break
        return dict(sorted(self._placed.items()))

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

    def update_pet_maintenance(self):
        """
        Recalculate maintenance_level for every pet based on their
        currently placed schedule tasks. Call this after generate_schedule().
        """
        for pet in self.user_pets:
            tasks = self.user_schedule.get_tasks_for_pet(pet.id)
            pet.update_maintenance_level(tasks)

    def add_constraint(self, label: str, start_time: str, end_time: str):
        """
        Block off a time range in the user's schedule for a named plan.

        Parameters
        ----------
        label      : str — description of the plan, e.g. 'Work', 'Gym', 'Dinner'
        start_time : str — start time, e.g. '9am', '1:30pm'
        end_time   : str — end time,   e.g. '5pm', '2:00pm'

        Converts the human-readable times to minutes and passes them to
        the schedule so generate_schedule() avoids that window.
        """
        start_min = Schedule._parse_time(start_time)
        end_min   = Schedule._parse_time(end_time)
        if end_min <= start_min:
            raise ValueError(
                f"End time '{end_time}' must be after start time '{start_time}'."
            )
        self.user_schedule.block_time(start_min, end_min)
        print(f"Constraint added: '{label}' from {Schedule._to_time(start_min)} "
              f"to {Schedule._to_time(end_min)}")


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create a user
    owner = User(id=1, name="Alex")

    # Create pets (maintenance_level is calculated automatically)
    dog = Pet(id=1, name="Buddy",    type="Dog", age=3)
    cat = Pet(id=2, name="Whiskers", type="Cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Add user constraints (plans that block time in the schedule)
    owner.add_constraint("Work",   start_time="9:00am", end_time="5:00pm")
    owner.add_constraint("Dinner", start_time="6:30pm", end_time="7:30pm")

    # Create tasks (duration in minutes)
    walk  = Task(task_name="Morning Walk",  duration=30, priority=5, pet_id=dog.id)
    feed  = Task(task_name="Feed Whiskers", duration=10, priority=4, pet_id=cat.id)
    groom = Task(task_name="Groom Buddy",   duration=20, priority=3, pet_id=dog.id)

    owner.user_schedule.add_task(walk)
    owner.user_schedule.add_task(feed)
    owner.user_schedule.add_task(groom)

    # Print user & pet info
    print(owner.view_user_info())
    print(dog.view_pet_info())
    print(cat.view_pet_info())

    # Generate schedule, then recalculate maintenance levels from placed tasks
    owner.user_schedule.generate_schedule()
    owner.update_pet_maintenance()

    print("\n--- Daily Schedule (12 AM – 12 AM) ---")
    owner.user_schedule.view_schedule()

    print("\n--- Pet Maintenance Levels (post-schedule) ---")
    print(dog.view_pet_info())
    print(cat.view_pet_info())
