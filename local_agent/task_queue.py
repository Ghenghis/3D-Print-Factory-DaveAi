"""
DaveAI Task Queue — lightweight in-process task queue with JSONL history.
"""

import json
import threading
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class Task:
    def __init__(self, name: str, fn: Callable, args: tuple = (), kwargs: dict = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs or {}
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.started_at = None
        self.finished_at = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


class TaskQueue:
    def __init__(self, history_file: str = "proof/windsurf/local-agent/task-history.jsonl"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._tasks: dict[str, Task] = {}
        self._lock = threading.Lock()

    def submit(self, name: str, fn: Callable, args: tuple = (), kwargs: dict = None) -> Task:
        task = Task(name, fn, args, kwargs)
        with self._lock:
            self._tasks[task.id] = task
        thread = threading.Thread(target=self._run, args=(task,), daemon=True)
        thread.start()
        return task

    def _run(self, task: Task) -> None:
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()
        self._log(task)
        try:
            task.result = task.fn(*task.args, **task.kwargs)
            task.status = TaskStatus.DONE
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        finally:
            task.finished_at = datetime.now(timezone.utc).isoformat()
            self._log(task)

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def all_tasks(self) -> list:
        return [t.to_dict() for t in self._tasks.values()]

    def _log(self, task: Task) -> None:
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(task.to_dict()) + "\n")
