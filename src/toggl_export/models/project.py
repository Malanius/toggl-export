from collections import defaultdict
from dataclasses import dataclass, field

from loguru import logger

from toggl_export import config
from toggl_export.models.time_entry import TimeEntry

SECONDS_IN_HOUR = 3600


@dataclass
class Project:
    id: int
    name: str
    time_worked: int = 0
    tasks: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def add_entry(self, entry: TimeEntry):
        duration = entry["duration"]
        self.time_worked += duration
        task_description = self._get_task_description(entry)
        self.tasks[task_description] += duration
        logger.debug(f"Added project entry: {entry['description']}")

    @property
    def worked_hours(self):
        return self.time_worked / SECONDS_IN_HOUR

    def print(self, hide_time) -> str:
        time_spent = f": {self.worked_hours:.2f}h" if not hide_time else ""
        s = f"[cyan]{self.name}{time_spent}[/cyan]\n"

        for task_name, worked_seconds in self.tasks.items():
            s += f"{task_name}"
            if not hide_time:
                s += f": [magenta]{worked_seconds / SECONDS_IN_HOUR:.2f}h[/magenta]"
            s += "\n"
        s += "\n"

        return s

    def _get_task_description(self, entry: TimeEntry):
        full_description = entry["description"]
        return full_description[full_description.rfind(config.PROJECT_SEPARATOR) :]
