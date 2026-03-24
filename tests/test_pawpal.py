import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task


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
