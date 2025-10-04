import datetime as dt
from enum import Enum
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

HOME = Path.home()
CD = Path(__file__).parent
APP_DIR = HOME / ".task_cli"
APP_DIR.mkdir(exist_ok=True)
JSON_PATH = APP_DIR / "tasks_tracker.json"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


@dataclass
class Task:
    id: int
    description: str
    status: str = "todo"
    created_at: dt.datetime = field(default_factory=dt.datetime.now)
    updated_at: dt.datetime = field(default_factory=dt.datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TaskManager:
    def __init__(self, json_path: Path = JSON_PATH):
        self.json_path: Path = json_path
        self.last_id: int = 0
        self.tasks: list[Task] = []
        self._load()

    def _open_data(self) -> dict:
        with open(self.json_path, "r") as f:
            data = json.load(f)
        return data

    def _write_data(self, data: dict) -> None:
        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load(self) -> None:
        if not self.json_path.exists():
            # File doesn’t exist, create empty structure
            self.tasks = []
            self.last_id = 0
            self._write_data({"last_id": self.last_id, "tasks": self.tasks})
            return

        try:
            data = self._open_data()
            self.last_id = data.get("last_id", 0)
            self.tasks = [
                Task(
                    id=task["id"],
                    description=task["description"],
                    status=task["status"],
                    created_at=dt.datetime.fromisoformat(task["created_at"]),
                    updated_at=dt.datetime.fromisoformat(task["updated_at"]),
                )
                for task in data.get("tasks", [])
            ]
        except (json.JSONDecodeError, KeyError):
            self._write_data({"last_id": 0, "tasks": []})
            self.last_id = 0
            self.tasks = []

    def save(self) -> None:
        data = {
            "last_id": self.last_id,
            "tasks": [task.to_dict() for task in self.tasks],
        }
        self._write_data(data)

    def add(self, description: str) -> None:
        self.last_id += 1
        task = Task(id=self.last_id, description=description)
        self.tasks.append(task)
        self.save()
        logger.info(f"Task added successfully (ID: {task.id})")

    def _get_task(self, id: int) -> Task:
        if not self.tasks:
            raise ValueError(
                "No tasks yet. Run ```task_cli add 'description here'``` to add a task."
            )
        for task in self.tasks:
            if task.id == id:
                return task
        raise ValueError(f"No task found with ID {id}.")

    def update(self, id: int, description: str) -> None:
        task = self._get_task(id)
        task.description = description
        task.updated_at = dt.datetime.now()
        self.save()

    def delete(self, id: int) -> None:
        task = self._get_task(id)
        self.tasks.remove(task)
        self.save()

    def set_status(self, id: int, status: TaskStatus) -> None:
        if not isinstance(status, TaskStatus):
            raise ValueError("Status should be one of 'todo', 'in-progress' or 'done'.")

        task = self._get_task(id)
        task.status = status
        self.save()
        logger.info(f"Task {id} marked as {status.value}.")

    def list_tasks(self) -> list[str]:
        tasks = [
            f"{task.id}: {task.description} - {task.status}" for task in self.tasks
        ]
        return tasks


def main():
    task_manager = TaskManager()
    try:
        action = sys.argv[1]
    except IndexError:
        logger.error("No action provided. Usage: task_cli <action> [args]")
        return

    try:
        if action == "add":
            description = sys.argv[2]
            task_manager.add(description=description)
        elif action == "update":
            task_id = int(sys.argv[2])
            description = sys.argv[3]
            task_manager.update(task_id, description)
            logger.info(f"Task {task_id} updated successfully.")
        elif action == "delete":
            task_id = int(sys.argv[2])
            task_manager.delete(task_id)
            logger.info(f"Task {task_id} deleted successfully.")
        elif action.startswith("mark-"):
            raw_status = action[5:]
            try:
                task_status = TaskStatus(raw_status)
            except ValueError:
                logger.error(
                    f"Invalid status '{raw_status}'. Must be one of {[s.value for s in TaskStatus]}."
                )
                return
            task_id = int(sys.argv[2])
            task_manager.set_status(task_id, task_status)
        elif action == "list":
            tasks = task_manager.list_tasks()
            print("\n".join(tasks))
        else:
            logger.error(f"Unknown action '{action}'")

    except ValueError as e:
        # This will catch invalid task IDs or missing tasks
        logger.error(f"Error: {e}")

    except IndexError:
        # This will catch missing arguments
        logger.error("Missing arguments for the action.")


if __name__ == "__main__":
    main()
