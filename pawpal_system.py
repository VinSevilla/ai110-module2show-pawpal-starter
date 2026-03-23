from dataclasses import dataclass
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
    maintenance_level: int  # 1 (low) to 5 (high)

    def edit_pet_info(self, name: str = None, type: str = None,
                      age: int = None, maintenance_level: int = None):
        """Update one or more fields on this pet."""
        if name is not None:
            self.name = name
        if type is not None:
            self.type = type
        if age is not None:
            self.age = age
        if maintenance_level is not None:
            self.maintenance_level = maintenance_level

    def view_pet_info(self) -> str:
        """Return a formatted string of this pet's details."""
        return (
            f"[Pet #{self.id}] {self.name} | Type: {self.type} | "
            f"Age: {self.age} | Maintenance Level: {self.maintenance_level}"
        )


@dataclass
class Task:
    id: int
    name: str
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
# Schedule — manages tasks and generates a daily care plan
# ---------------------------------------------------------------------------

class Schedule:
    def __init__(self, time_constraints: List[str] = None):
        self.time_constraints: List[str] = time_constraints or []
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """Add a care task to the schedule."""
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        """Remove a task from the schedule by its ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def generate_schedule(self) -> List[Task]:
        """
        Return tasks sorted by priority (highest first).
        Respects time_constraints — extend this logic as needed.
        """
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)


# ---------------------------------------------------------------------------
# User — the pet owner, ties everything together
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create a user
    owner = User(id=1, name="Alex")

    # Create pets
    dog = Pet(id=1, name="Buddy", type="Dog", age=3, maintenance_level=4)
    cat = Pet(id=2, name="Whiskers", type="Cat", age=5, maintenance_level=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks
    walk  = Task(id=1, name="Morning Walk",  duration=30, priority=5, pet_id=dog.id)
    feed  = Task(id=2, name="Feed Whiskers", duration=10, priority=4, pet_id=cat.id)
    groom = Task(id=3, name="Groom Buddy",   duration=20, priority=3, pet_id=dog.id)

    # Build schedule
    owner.user_schedule.add_task(walk)
    owner.user_schedule.add_task(feed)
    owner.user_schedule.add_task(groom)

    # View results
    print(owner.view_user_info())
    print(dog.view_pet_info())
    print(cat.view_pet_info())

    print("\nGenerated Schedule (highest priority first):")
    for task in owner.user_schedule.generate_schedule():
        print(f"  - [{task.priority}] {task.name} ({task.duration} min)")
