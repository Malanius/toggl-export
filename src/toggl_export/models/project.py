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
    tasks: set[tuple[str, int]] = field(default_factory=set)

    def add_entry(self, entry: TimeEntry):
        duration = entry["duration"]
        self.time_worked += duration
        task_description = self._get_task_description(entry)
        self.tasks.add((task_description, duration))
        logger.debug(f"Added project entry: {entry['description']}")

    @property
    def worked_hours(self):
        return self.time_worked / SECONDS_IN_HOUR

    def print(self, hide_time) -> str:
        time_spent = f": {self.worked_hours:.2f}h" if not hide_time else ""
        s = f"[cyan]{self.name}{time_spent}[/cyan]\n"

        for task in self.tasks:
            s += f"{task[0]}"
            if not hide_time:
                s += f": [magenta]{task[1] / SECONDS_IN_HOUR:.2f}h[/magenta]"
            s += "\n"
        s += "\n"

        return s

    def _get_task_description(self, entry: TimeEntry):
        full_description = entry["description"]
        return full_description[full_description.rfind(config.PROJECT_SEPARATOR) :]
