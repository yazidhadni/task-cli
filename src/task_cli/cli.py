import argparse
import datetime as dt
from enum import Enum
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

HOME = Path.home()
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
    status: TaskStatus = TaskStatus.TODO
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

    def add(self, description: str) -> Task:
        self.last_id += 1
        task = Task(id=self.last_id, description=description)
        self.tasks.append(task)
        self.save()
        return task

    def _get_task(self, id: int) -> Task:
        if not self.tasks:
            raise ValueError(
                "No tasks yet. Run ```task_cli add 'description here'``` to add a task."
            )
        for task in self.tasks:
            if task.id == id:
                return task
        raise ValueError(f"No task found with ID {id}.")

    def update(self, id: int, description: str) -> Task:
        task = self._get_task(id)
        task.description = description
        task.updated_at = dt.datetime.now()
        self.save()
        return task

    def delete(self, id: int) -> Task:
        task = self._get_task(id)
        self.tasks.remove(task)
        self.save()
        return task

    def set_status(self, id: int, status: TaskStatus) -> Task:
        if not isinstance(status, TaskStatus):
            raise ValueError("Status should be one of 'todo', 'in-progress' or 'done'.")

        task = self._get_task(id)
        task.status = status
        self.save()
        return task

    def list_tasks(self) -> list[str]:
        tasks = [
            f"{task.id}: {task.description} - {task.status}" for task in self.tasks
        ]
        return tasks


def log_verbose(message: str, verbose: bool):
    if verbose:
        logger.info(message)


def main():
    task_manager = TaskManager()

    parser = argparse.ArgumentParser(
        description="Task CLI: manage your tasks from the terminal"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    # add
    add_parser = subparsers.add_parser("add", help="Add new task")
    add_parser.add_argument("description", help="Description of the task")
    # update
    update_parser = subparsers.add_parser("update", help="Update task")
    update_parser.add_argument("id", type=int, help="ID of the task")
    update_parser.add_argument("description", help="Description of the task")
    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete task")
    delete_parser.add_argument("id", type=int, help="ID of the task")
    # list
    subparsers.add_parser("list", help="List all tasks")
    # mark: change task status
    mark_parser = subparsers.add_parser("mark", help="change task status")
    mark_parser.add_argument("id", type=int, help="ID of the task")
    mark_parser.add_argument(
        "status",
        choices=["todo", "in-progress", "done"],
        help="Status to mark the task",
    )

    args = parser.parse_args()

    if args.command == "add":
        task = task_manager.add(args.description)
        log_verbose(f"Task added successfully (ID: {task.id}).", args.verbose)

    elif args.command == "update":
        task = task_manager.update(id=args.id, description=args.description)
        log_verbose(f"Task {task.id} updated successfully.", args.verbose)

    elif args.command == "delete":
        task = task_manager.delete(args.id)
        log_verbose(f"Task {task.id} deleted successfully.", args.verbose)

    elif args.command == "list":
        tasks = task_manager.list_tasks()
        print("\n".join(tasks))
        log_verbose(f"Listed {len(tasks)} tasks", args.verbose)

    elif args.command == "mark":
        task = task_manager.set_status(id=args.id, status=TaskStatus(args.status))
        log_verbose(f"Task {task.id} marked as {task.status.value}", args.verbose)


if __name__ == "__main__":
    main()
