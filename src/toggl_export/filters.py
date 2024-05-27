from toggl_export.models.time_entry import TimeEntry


def filter_by_workspace(entries: list[TimeEntry], workspace_id: str) -> list[TimeEntry]:
    return [entry for entry in entries if entry["workspace_id"] == int(workspace_id)]

