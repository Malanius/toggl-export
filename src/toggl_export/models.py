from typing import List, TypedDict


class TimeEntry(TypedDict):
    id: int
    wid: int
    pid: int
    billable: bool
    start: str
    stop: str
    duration: int
    description: str
    tags: List[str]
    at: str
