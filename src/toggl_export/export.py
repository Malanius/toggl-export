from collections import defaultdict
from datetime import datetime
from typing import List
import os

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from toggl_export.arguments import init_arguments
from toggl_export.models import TimeEntry

load_dotenv()
TOKEN = os.getenv("API_TOKEN")

API_BASE_URL = "https://api.track.toggl.com/api/v8"
TIME_ENTRIES_ENDPOINT = "time_entries"


def get_time_entries(start_date, end_date) -> List[TimeEntry]:
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
    # print(f"Url: {request.url}")
    # print(f"Status: {request.status_code}")
    if request.ok:
        return request.json()


def group_by_day(entries: List[TimeEntry]):
    day_entries = defaultdict(list)
    for entry in entries:
        start_day = entry["start"][:10]
        day_entries[start_day].append(entry)
    return day_entries


def group_by_project(entries: List[TimeEntry]):
    project_entries = defaultdict(list)
    for entry in entries:
        project = entry["pid"]
        project_entries[project].append(entry)
    return project_entries


def print_entries(day: str, projects_entries: dict[int, List[TimeEntry]]):
    print(f"--- {day} ---")
    for project_entries in projects_entries.values():
        project = {
            entry["description"][: entry["description"].find(" - ")]
            for entry in project_entries
        }.pop()
        durations = [entry["duration"] for entry in project_entries]
        spent_time = sum(durations) / 60 / 60  # durations are in seconds
        print(f"{project}: {spent_time}")
        for entry in project_entries:
            full_description = entry["description"]
            task_description = full_description[full_description.rfind(" - ") :]
            print(f"{task_description}")
        print("\n")


def main():
    args = init_arguments()
    entries = get_time_entries(args.start, args.end)
    entries_by_day = group_by_day(entries)
    grouped_entries = {}
    for day, day_entries in entries_by_day.items():
        grouped_entries[day] = group_by_project(day_entries)
    for day, projects_entries in grouped_entries.items():
        print_entries(day, projects_entries)


if __name__ == "__main__":
    main()
