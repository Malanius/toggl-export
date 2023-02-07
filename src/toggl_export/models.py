from typing import List, TypedDict


class TimeEntry(TypedDict):
    id: int
    workspace_id: int
    project_id: int
    billable: bool
    start: str
    stop: str
    duration: int
    description: str
    tags: List[str]
    at: str
