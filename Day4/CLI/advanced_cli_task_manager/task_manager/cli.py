import argparse
from task_manager.core import add_task, list_tasks, delete_task
from task_manager.logger import setup_logger

logger = setup_logger()


def main():
    parser = argparse.ArgumentParser(description="CLI Task Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add Task
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Description of the task")
    add_parser.add_argument(
        "--priority", choices=["low", "medium", "high"], default="medium",
        help="Priority of the task (default: medium)"
    )

    # List Tasks
    subparsers.add_parser("list", help="List all tasks")

    # Delete Task
    delete_parser = subparsers.add_parser("delete", help="Delete a task by id")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")

    args = parser.parse_args()

    if args.command == "add":
        task = add_task(args.description, args.priority)
        print(f"Added task #{task['id']}: {task['description']} (priority={task['priority']})")

    elif args.command == "list":
        tasks = list_tasks()
        if not tasks:
            print("No tasks found.")
        for t in tasks:
            status = "✔" if t["done"] else "✘"
            print(f"[{status}] #{t['id']} {t['description']} (priority={t['priority']})")

    elif args.command == "delete":
        if delete_task(args.task_id):
            print(f"Deleted task #{args.task_id}")
        else:
            print(f"Task #{args.task_id} not found")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
