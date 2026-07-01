# CLI Task Manager

A simple command-line task manager built with `argparse`, storing tasks in a JSON file.

## Usage

```bash
python -m task_manager.cli add "Buy milk" --priority high
python -m task_manager.cli list
python -m task_manager.cli delete 1
```

## Configuration

Set the `TASKS_FILE_PATH` environment variable to change where tasks are stored:

```bash
export TASKS_FILE_PATH=my_tasks.json
```

## Tests

```bash
python -m unittest tests/test_core.py
```
