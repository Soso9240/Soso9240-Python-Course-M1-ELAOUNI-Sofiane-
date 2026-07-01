import json
import os

from task_manager.logger import setup_logger
from task_manager.config import TASKS_FILE

logger = setup_logger()


def load_tasks():
    """Load tasks from the JSON file. Returns an empty list if the file doesn't exist."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("Tasks file is corrupted, starting with an empty list.")
        return []


def save_tasks(tasks):
    """Save the list of tasks to the JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def add_task(description, priority="medium"):
    """Add a new task and return it."""
    tasks = load_tasks()
    new_id = (max((t["id"] for t in tasks), default=0)) + 1
    task = {
        "id": new_id,
        "description": description,
        "priority": priority,
        "done": False,
    }
    tasks.append(task)
    save_tasks(tasks)
    logger.info(f"Added task {new_id}: {description} (priority={priority})")
    return task


def list_tasks():
    """Return all tasks."""
    tasks = load_tasks()
    logger.info(f"Listed {len(tasks)} task(s)")
    return tasks


def delete_task(task_id):
    """Delete a task by id. Returns True if deleted, False if not found."""
    tasks = load_tasks()
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        logger.warning(f"Tried to delete non-existent task {task_id}")
        return False
    save_tasks(remaining)
    logger.info(f"Deleted task {task_id}")
    return True
