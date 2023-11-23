import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv
from loguru import logger
from requests.auth import HTTPBasicAuth

from toggl_export.arguments import init_arguments
from toggl_export.models.time_entry import TimeEntry
from toggl_export.models.workday import Workday

load_dotenv()
TOKEN = os.getenv("API_TOKEN") or ""
PROJECT_SEPARATOR = os.getenv("PROJECT_SEPARATOR") or " | "
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL") or "INFO"

API_BASE_URL = "https://api.track.toggl.com/api/v9/me"
TIME_ENTRIES_ENDPOINT = "time_entries"

logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)


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
    logger.debug(f"Url: {request.url}")
    if request.ok:
        logger.debug(f"Status: {request.status_code}")
        return request.json()
    else:
        logger.debug(f"Status: {request.status_code}")
        request.raise_for_status()
        raise Exception("Error retrieving time entries!")


def filter_by_workspace(entries: list[TimeEntry]):
    if WORKSPACE_ID is None:
        return entries

    return [entry for entry in entries if entry["workspace_id"] == int(WORKSPACE_ID)]


def convert_to_eod(date):
    return datetime.combine(
        datetime.fromisoformat(date), datetime.max.time()
    ).isoformat()


workdays: dict[str, Workday] = {}


def main():
    args = init_arguments()
    start = args.start
    end = convert_to_eod(args.end)
    entries = get_time_entries(start, end)
    filtered_entries = filter_by_workspace(entries)
    sorted_entries = sorted(filtered_entries, key=lambda entry: entry["start"])

    for entry in sorted_entries:
        day = entry["start"][:10]

        if day not in workdays:
            workday = Workday(date=day)
            workdays[day] = workday
            logger.debug(f"Created new workday: {day}")
        else:
            workday = workdays[day]

        workday.add_entry(entry)
        logger.debug(f"Added entry to existing workday: {day}")

    for workday in workdays.values():
        workday.print()


if __name__ == "__main__":
    main()
