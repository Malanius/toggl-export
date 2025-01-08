from dataclasses import dataclass, field

from loguru import logger
from rich import print as rprint
from toggl_export import config
from toggl_export.models.project import Project
from toggl_export.models.time_entry import TimeEntry

SECONDS_IN_HOUR = 3600


@dataclass
class Workday:
    date: str
    time_worked: int = 0
    worked_projects: dict[int, Project] = field(default_factory=dict)

    def add_entry(self, entry: TimeEntry):
        self.time_worked += entry["duration"]

        project_id = entry["project_id"]
        if project_id not in self.worked_projects:
            self._create_project(entry)

        self.worked_projects[project_id].add_entry(entry)
        logger.debug(f"Added entry to project {self.worked_projects[project_id].name}")

    @property
    def worked_hours(self):
        return self.time_worked / SECONDS_IN_HOUR

    def print(self, hide_time) -> str:
        worked_hours = f"{self.worked_hours:.2f}h" if not hide_time else ""
        s: str = f"[yellow bold]--- {self.date}: {worked_hours} ---[/yellow bold]\n"
        for project in self.worked_projects.values():
            s = s + project.print(hide_time)
        return s

    def _create_project(self, entry: TimeEntry):
        project_id = entry["project_id"]
        project_name = entry["description"][
            : entry["description"].find(config.PROJECT_SEPARATOR)
        ]
        self.worked_projects[project_id] = Project(
            id=project_id,
            name=project_name,
        )
        logger.debug(f"Created new project {project_name} for workday {self.date}")
