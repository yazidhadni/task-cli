# Task Tracker CLI

A simple command-line interface (CLI) application to track and manage your tasks and to-do list. This tool lets you add, update, delete, and mark tasks as in progress or done, while keeping your data persistent in a JSON file.  

---

## Features

- Add new tasks  
- Update existing tasks  
- Delete tasks  
- Mark tasks as **in-progress** or **done** (to be implemented)  
- List all tasks or filter by status (to be implemented)  
- Persistent storage in a JSON file located in `~/.task_cli/tasks_tracker.json`  

---

## Task Properties

Each task includes:

- `id`: Unique identifier  
- `description`: Short description of the task  
- `status`: `todo`, `in-progress`, or `done`  
- `created_at`: Timestamp when the task was created  
- `updated_at`: Timestamp of the last modification  

---

## Notes
- Tasks are stored in ~/.task_cli/tasks_tracker.json for persistence.
- IDs are unique and never reused, even if tasks are deleted.
- CLI handles invalid IDs and missing arguments gracefully.

## Next Steps (Planned)
- Mark tasks as in-progress or done
- List tasks filtered by status
- Add a list command to display all tasks
- Improve CLI UX with argument validation and help command