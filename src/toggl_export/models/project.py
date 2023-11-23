import os
from dataclasses import dataclass, field

from loguru import logger
from rich import print as rprint
from toggl_export.models.time_entry import TimeEntry

PROJECT_SEPARATOR = os.getenv("PROJECT_SEPARATOR") or " | "


@dataclass
class Project:
    id: int
    name: str
    time_worked: int = 0
    entries: list[TimeEntry] = field(default_factory=list)

    def add_entry(self, entry: TimeEntry):
        self.time_worked += entry["duration"]
        self.entries.append(entry)
        logger.debug(f"Added project entry: {entry['description']}")

    def _work_hours(self):
        return self.time_worked / 60 / 60

    def print(self):
        rprint(f"[cyan]{self.name}: {self._work_hours()}h")
        tasks_set = set()

        for entry in self.entries:
            full_description = entry["description"]
            task_description = full_description[
                full_description.rfind(PROJECT_SEPARATOR) :
            ]
            tasks_set.add(task_description)

        for task in tasks_set:
            print(f"{task}")
