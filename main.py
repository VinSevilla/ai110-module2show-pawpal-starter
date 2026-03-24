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

    owner.add_constraint("Work", start_time="9:00am", end_time="5:00pm")

    # -----------------------------------------------------------------------
    # Add tasks OUT OF ORDER to prove sort_by_time() fixes the display
    # (Evening tasks added before morning tasks intentionally)
    # -----------------------------------------------------------------------
    evening_walk = Task(task_name="Evening Walk",   duration=30, priority=3, pet_id=dog.id)
    night_feed   = Task(task_name="Night Feed Cat", duration=10, priority=2, pet_id=cat.id)
    morning_walk = Task(task_name="Morning Walk",   duration=30, priority=5, pet_id=dog.id)
    morning_feed = Task(task_name="Morning Feed",   duration=10, priority=5, pet_id=cat.id)
    groom        = Task(task_name="Groom Buddy",    duration=20, priority=4, pet_id=dog.id)
    evening_feed = Task(task_name="Evening Feed",   duration=10, priority=3, pet_id=cat.id,
                        recurring=False)

    # Add in deliberately jumbled order
    owner.user_schedule.add_task(evening_walk)   # added first, should appear last
    owner.user_schedule.add_task(night_feed)
    owner.user_schedule.add_task(morning_walk)   # added third, should appear first
    owner.user_schedule.add_task(morning_feed)
    owner.user_schedule.add_task(groom)
    owner.user_schedule.add_task(evening_feed)

    # -----------------------------------------------------------------------
    # Generate schedule
    # -----------------------------------------------------------------------
    owner.user_schedule.generate_schedule()
    owner.update_pet_maintenance()

    # -----------------------------------------------------------------------
    # sort_by_time() — tasks in chronological order regardless of add order
    # -----------------------------------------------------------------------
    print("=== Full Schedule (sorted by time) ===")
    for start_min, task in owner.user_schedule.sort_by_time():
        end_min = start_min + task.duration
        print(
            f"  {Schedule._to_time(start_min)} – {Schedule._to_time(end_min)}"
            f"  [{task.priority}★] {task.task_name}  ({task.status})"
        )

    # -----------------------------------------------------------------------
    # filter_tasks_by_pet_name() — show only Buddy's tasks
    # -----------------------------------------------------------------------
    print("\n=== Buddy's Tasks Only ===")
    for task in owner.filter_tasks_by_pet_name(pet_name="Buddy"):
        print(f"  {task.task_name} ({task.duration} min, priority {task.priority})")

    # -----------------------------------------------------------------------
    # filter_tasks(status=) — mark one task complete, then show pending only
    # -----------------------------------------------------------------------
    morning_walk.mark_complete()

    print("\n=== Pending Tasks Only (after marking Morning Walk complete) ===")
    for task in owner.user_schedule.filter_tasks(status="pending"):
        print(f"  {task.task_name}  [{task.status}]")

    # -----------------------------------------------------------------------
    # check_conflicts() — report anything that didn't fit
    # -----------------------------------------------------------------------
    conflicts = owner.user_schedule.check_conflicts()
    print("\n=== Conflicts (tasks that couldn't be placed) ===")
    if conflicts:
        for task in conflicts:
            print(f"  ✗ {task.task_name}")
    else:
        print("  None — all tasks fit in the schedule.")

    # -----------------------------------------------------------------------
    # Maintenance levels (auto-calculated from placed tasks)
    # -----------------------------------------------------------------------
    print("\n=== Pet Maintenance Levels ===")
    print(dog.view_pet_info())
    print(cat.view_pet_info())
