from pawpal_system import User, Pet, Task, Schedule

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Setup
    # -----------------------------------------------------------------------
    owner = User(id=1, name="Alex")
    dog = Pet(id=1, name="Buddy",    type="Dog", age=3)
    cat = Pet(id=2, name="Whiskers", type="Cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    schedule = owner.user_schedule

    # -----------------------------------------------------------------------
    # Force two tasks at the same time to create a conflict
    # Morning Walk (30 min) and Feed Whiskers (10 min) both start at 8:00 AM
    # -----------------------------------------------------------------------
    walk = Task(task_name="Morning Walk",   duration=30, priority=5, pet_id=dog.id)
    feed = Task(task_name="Feed Whiskers",  duration=10, priority=5, pet_id=cat.id)
    groom = Task(task_name="Groom Buddy",   duration=20, priority=4, pet_id=dog.id)

    # add_task_at() bypasses conflict checking so we can deliberately overlap
    schedule.add_task_at(walk,  "8:00am")   # 8:00 AM – 8:30 AM
    schedule.add_task_at(feed,  "8:15am")   # 8:15 AM – 8:25 AM  ← overlaps walk
    schedule.add_task_at(groom, "9:00am")   # 9:00 AM – 9:20 AM  ← no overlap

    # -----------------------------------------------------------------------
    # Print the raw schedule before conflict check
    # -----------------------------------------------------------------------
    print("=== Schedule (before conflict check) ===")
    for start_min, task in schedule.sort_by_time():
        end_min = start_min + task.duration
        print(f"  {Schedule._to_time(start_min)} – {Schedule._to_time(end_min)}  {task.task_name}")

    # -----------------------------------------------------------------------
    # Lightweight conflict detection — warns, never crashes
    # -----------------------------------------------------------------------
    print("\n=== Conflict Detection ===")
    conflicts = schedule.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")

    # -----------------------------------------------------------------------
    # Same pet, same time — more specific scenario
    # -----------------------------------------------------------------------
    print("\n--- Same-pet overlap scenario ---")
    schedule2 = Schedule()
    walk2  = Task(task_name="Morning Walk",   duration=45, priority=5, pet_id=dog.id)
    walk3  = Task(task_name="Training Run",   duration=30, priority=4, pet_id=dog.id)
    schedule2.add_task_at(walk2, "7:00am")   # 7:00 – 7:45 AM
    schedule2.add_task_at(walk3, "7:30am")   # 7:30 – 8:00 AM  ← overlaps walk2 (same pet)

    for warning in schedule2.detect_conflicts():
        print(f"  {warning}")
