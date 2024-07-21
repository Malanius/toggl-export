from typing import TypedDict


class TimeEntry(TypedDict):
    at: str
    billable: bool
    client_name: str
    description: str
    duration: int
    duronly: bool
    id: int
    project_active: bool
    project_color: str
    project_id: int
    project_name: str
    start: str
    stop: str
    tags: list[str]
    workspace_id: int
