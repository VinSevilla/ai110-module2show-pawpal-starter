import streamlit as st
from pawpal_system import User, Pet, Task, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — initialize once, survives reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner")
owner_name = st.text_input("Your name", value="Jordan")

if st.button("Create / Update Owner"):
    if st.session_state.owner is None:
        # First time — create a new User and store it in session state
        st.session_state.owner = User(id=1, name=owner_name)
    else:
        # Already exists — just update the name in place
        st.session_state.owner.edit_user_info(owner_name)
    st.success(f"Owner set to: {owner_name}")

owner = st.session_state.owner

if owner is None:
    st.info("Create an owner above to get started.")
    st.stop()  # Don't render anything below until an owner exists

st.divider()

# ---------------------------------------------------------------------------
# Add a Pet  →  owner.add_pet(Pet(...))
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    pet_type = st.selectbox("Species", ["Dog", "Cat", "Other"])
    pet_age  = st.number_input("Age", min_value=0, max_value=30, value=2)
    pet_submitted = st.form_submit_button("Add Pet")

if pet_submitted:
    new_pet = Pet(
        id=st.session_state.next_pet_id,
        name=pet_name,
        type=pet_type,
        age=int(pet_age)
    )
    owner.add_pet(new_pet)                  # <-- Pet class method
    st.session_state.next_pet_id += 1
    st.success(f"Added {pet_name} the {pet_type}!")

# Show current pets — re-rendered every rerun from session_state.owner.user_pets
if owner.user_pets:
    st.write("**Your pets:**")
    for p in owner.user_pets:
        st.write(f"- {p.name} ({p.type}, age {p.age})  |  Maintenance: {p.maintenance_level}/5")
else:
    st.info("No pets yet — add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Block off the owner's time  →  owner.add_constraint(...)
# ---------------------------------------------------------------------------
st.subheader("Block Off Your Time")

with st.form("constraint_form"):
    label      = st.text_input("Plan label (e.g. Work, Gym)", value="Work")
    start_time = st.text_input("Start time (e.g. 9:00am)", value="9:00am")
    end_time   = st.text_input("End time   (e.g. 5:00pm)", value="5:00pm")
    constraint_submitted = st.form_submit_button("Add Constraint")

if constraint_submitted:
    try:
        owner.add_constraint(label, start_time, end_time)   # <-- User class method
        st.success(f"Blocked '{label}' from {start_time} to {end_time}.")
    except ValueError as e:
        st.error(str(e))

st.divider()

# ---------------------------------------------------------------------------
# Add a Care Task  →  owner.user_schedule.add_task(Task(...))
# ---------------------------------------------------------------------------
st.subheader("Add a Care Task")

if not owner.user_pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_map = {p.name: p for p in owner.user_pets}

    with st.form("add_task_form"):
        task_name    = st.text_input("Task name", value="Morning Walk")
        duration     = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        priority     = st.slider("Priority (1 = low, 5 = high)", min_value=1, max_value=5, value=3)
        selected_pet = st.selectbox("For which pet?", list(pet_map.keys()))
        task_submitted = st.form_submit_button("Add Task")

    if task_submitted:
        pet = pet_map[selected_pet]
        new_task = Task(
            task_name=task_name,
            duration=int(duration),
            priority=priority,
            pet_id=pet.id
        )
        owner.user_schedule.add_task(new_task)    # <-- Schedule class method
        st.success(f"Task '{task_name}' added for {selected_pet}!")

    # Show the unscheduled task pool
    if owner.user_schedule.tasks:
        id_to_name = {p.id: p.name for p in owner.user_pets}
        st.write("**Task pool (not yet scheduled):**")
        for t in owner.user_schedule.tasks:
            st.write(
                f"- [Priority {t.priority}] {t.task_name} "
                f"({t.duration} min) — {id_to_name.get(t.pet_id, '?')}"
            )

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule  →  generate_schedule() + update_pet_maintenance()
# ---------------------------------------------------------------------------
st.subheader("Generate Daily Schedule")

if st.button("Generate Schedule"):
    if not owner.user_schedule.tasks:
        st.warning("Add some tasks first.")
    else:
        owner.user_schedule.generate_schedule()     # <-- Schedule class method
        owner.update_pet_maintenance()              # <-- User class method (updates maintenance_level)

        placed = owner.user_schedule._placed
        if placed:
            st.success("Schedule generated!")
            id_to_name = {p.id: p.name for p in owner.user_pets}
            rows = [
                {
                    "Time": f"{Schedule._to_time(start)} – {Schedule._to_time(start + t.duration)}",
                    "Task": t.task_name,
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Pet": id_to_name.get(t.pet_id, "?"),
                    "Status": t.status,
                }
                for start, t in sorted(placed.items())
            ]
            st.table(rows)

            st.write("**Updated Maintenance Levels:**")
            for p in owner.user_pets:
                st.write(f"- {p.name}: {p.maintenance_level}/5")
        else:
            st.warning("No tasks could be placed — all time slots may be blocked.")
