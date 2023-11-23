import os
from dataclasses import dataclass, field

from loguru import logger
from rich import print as rprint
from toggl_export.models.project import Project
from toggl_export.models.time_entry import TimeEntry

PROJECT_SEPARATOR = os.getenv("PROJECT_SEPARATOR") or " | "


@dataclass
class Workday:
    date: str
    time_worked: int = 0
    worked_projects: dict[int, Project] = field(default_factory=dict)

    def add_entry(self, entry: TimeEntry):
        self.time_worked += entry["duration"]

        project_id = entry["project_id"]
        if project_id not in self.worked_projects:
            project_name = entry["description"][
                : entry["description"].find(PROJECT_SEPARATOR)
            ]
            self.worked_projects[project_id] = Project(
                id=project_id,
                name=project_name,
            )
            logger.debug(f"Created new project {project_name} for workday {self.date}")

        self.worked_projects[project_id].add_entry(entry)
        logger.debug(f"Added entry to project {self.worked_projects[project_id].name}")

    def _work_hours(self):
        return self.time_worked / 60 / 60

    def print(self):
        rprint(f"[yellow bold]--- {self.date}: {self._work_hours():.2f}h ---")
        for project in self.worked_projects.values():
            project.print()
            print("\n")
