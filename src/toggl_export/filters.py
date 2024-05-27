from toggl_export.models.time_entry import TimeEntry


def filter_by_workspace(entries: list[TimeEntry], workspace_id: str) -> list[TimeEntry]:
    return [entry for entry in entries if entry["workspace_id"] == int(workspace_id)]

def filter_by_client(entries: list[TimeEntry], client_name: str) -> list[TimeEntry]:
    return [entry for entry in entries if entry["client_name"] == client_name]