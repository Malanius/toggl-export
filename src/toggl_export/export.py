import os
from collections import defaultdict
from datetime import datetime
from itertools import chain
from typing import Iterable

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from rich import print as rprint

from toggl_export.arguments import init_arguments
from toggl_export.models import TimeEntry

load_dotenv()
TOKEN = os.getenv("API_TOKEN") or ""
PROJECT_SEPARATOR = os.getenv("PROJECT_SEPARATOR") or "|"
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

API_BASE_URL = "https://api.track.toggl.com/api/v9/me"
TIME_ENTRIES_ENDPOINT = "time_entries"


def get_time_entries(start_date, end_date) -> list[TimeEntry]:
    start_datetime = datetime.fromisoformat(start_date).astimezone().isoformat()
    end_datetime = datetime.fromisoformat(end_date).astimezone().isoformat()
    range = {
        "start_date": f"{start_datetime}",
        "end_date": f"{end_datetime}",
    }
    request = requests.get(
        f"{API_BASE_URL}/{TIME_ENTRIES_ENDPOINT}",
        params=range,
        auth=HTTPBasicAuth(TOKEN, "api_token"),
    )
    print(f"Url: {request.url}")
    if request.ok:
        rprint(f"[green]Status: {request.status_code}")
        return request.json()
    else:
        rprint(f"[red]Status: {request.status_code}")
        request.raise_for_status()
        raise Exception("Error retrieving time entries!")


def filter_by_workspace(entries: list[TimeEntry]):
    if WORKSPACE_ID is None:
        return entries

    return [entry for entry in entries if entry["workspace_id"] == int(WORKSPACE_ID)]


def group_by_day(entries: list[TimeEntry]):
    day_entries = defaultdict(list)
    for entry in entries:
        start_day = entry["start"][:10]
        day_entries[start_day].append(entry)
    return day_entries


def calculate_daily_hours(entries: Iterable[TimeEntry]):
    return sum(entry["duration"] for entry in entries) / 60 / 60


def group_by_project(entries: list[TimeEntry]):
    project_entries = defaultdict(list)
    for entry in entries:
        project = entry["project_id"]
        project_entries[project].append(entry)
    return project_entries


def print_entries(day: str, projects_entries: dict[int, list[TimeEntry]]):
    day_hours = calculate_daily_hours(chain(*projects_entries.values()))
    rprint(f"[yellow bold]--- {day}: {day_hours}h ---")
    for project_entries in projects_entries.values():
        project = {
            entry["description"][: entry["description"].find(PROJECT_SEPARATOR)]
            for entry in project_entries
        }.pop()
        durations = [entry["duration"] for entry in project_entries]
        spent_time = sum(durations) / 60 / 60  # durations are in seconds
        rprint(f"[cyan]{project}: {spent_time}h")
        tasks_set = set()
        for entry in project_entries:
            full_description = entry["description"]
            task_description = full_description[
                full_description.rfind(PROJECT_SEPARATOR) :
            ]
            tasks_set.add(task_description)
        for task in tasks_set:
            print(f"{task}")
        print("\n")


def convert_to_eod(date):
    return datetime.combine(
        datetime.fromisoformat(date), datetime.max.time()
    ).isoformat()


def main():
    args = init_arguments()
    start = args.start
    end = convert_to_eod(args.end)
    entries = get_time_entries(start, end)
    filtered_entries = filter_by_workspace(entries)
    entries_by_day = group_by_day(filtered_entries)
    grouped_entries = {}
    for day, day_entries in entries_by_day.items():
        grouped_entries[day] = group_by_project(day_entries)
    for day, projects_entries in reversed(grouped_entries.items()):
        print_entries(day, projects_entries)


if __name__ == "__main__":
    main()
