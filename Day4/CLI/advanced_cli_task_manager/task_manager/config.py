import os

# Path to the JSON file used to store tasks.
# Can be overridden with the TASKS_FILE_PATH environment variable.
TASKS_FILE = os.getenv("TASKS_FILE_PATH", "tasks.json")
