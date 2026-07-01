import os
import unittest

os.environ["TASKS_FILE_PATH"] = "test_tasks.json"

from task_manager.core import add_task, load_tasks, delete_task


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # Start each test with a clean tasks file
        if os.path.exists("test_tasks.json"):
            os.remove("test_tasks.json")

    def tearDown(self):
        if os.path.exists("test_tasks.json"):
            os.remove("test_tasks.json")

    def test_add_task(self):
        task = add_task("Write unit tests", priority="high")
        tasks = load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["description"], "Write unit tests")
        self.assertEqual(tasks[0]["priority"], "high")
        self.assertEqual(task["id"], 1)

    def test_delete_task(self):
        task = add_task("Temporary task")
        deleted = delete_task(task["id"])
        self.assertTrue(deleted)
        self.assertEqual(load_tasks(), [])

        # Deleting a non-existent task should return False
        self.assertFalse(delete_task(999))


if __name__ == "__main__":
    unittest.main()
