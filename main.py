from pawpal_system import Pet, Task, Schedule, User

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