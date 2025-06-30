from rich import print as rprint
from datetime import datetime

from toggl_export.models.time_entry import TimeEntry


def filter_by_workspace(entries: list[TimeEntry], workspace_id: str) -> list[TimeEntry]:
    return [entry for entry in entries if entry["workspace_id"] == int(workspace_id)]


def filter_by_client(entries: list[TimeEntry], client_name: str) -> list[TimeEntry]:
    for entry in entries:
        if not entry.get("client_name"):
            entry_date = datetime.fromisoformat(entry["start"]).strftime("%Y-%m-%d")
            rprint(
                f"[red] Entry \"{entry['description']}\" from {entry_date} does not have project or client information!"
            )
            exit(1)
    return [entry for entry in entries if entry["client_name"] == client_name]
