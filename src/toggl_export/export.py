import sys
from datetime import date, datetime

import requests
from loguru import logger
from requests.auth import HTTPBasicAuth

from toggl_export import config
from toggl_export.arguments import init_arguments
from toggl_export.models.time_entry import TimeEntry
from toggl_export.models.workday import Workday

API_BASE_URL = "https://api.track.toggl.com/api/v9/me"
TIME_ENTRIES_ENDPOINT = "time_entries"

logger.remove()
logger.add(sys.stderr, level=config.LOG_LEVEL)


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
        auth=HTTPBasicAuth(config.TOKEN, "api_token"),
    )
    logger.debug(f"Url: {request.url}")
    if request.ok:
        logger.debug(f"Status: {request.status_code}")
        return request.json()
    else:
        logger.debug(f"Status: {request.status_code}")
        request.raise_for_status()
        raise Exception("Error retrieving time entries!")


def filter_by_workspace(entries: list[TimeEntry], workspace_id: str) -> list[TimeEntry]:
    return [entry for entry in entries if entry["workspace_id"] == int(workspace_id)]


def convert_to_sod(date: date):
    return datetime.combine(date, datetime.min.time()).isoformat()

def convert_to_eod(date: date):
    return datetime.combine(date, datetime.max.time()).isoformat()


workdays: dict[str, Workday] = {}


def main():
    args = init_arguments()
    start = convert_to_sod(args.start)
    end = convert_to_eod(args.end)
    entries = get_time_entries(start, end)

    if config.WORKSPACE_ID:
        entries = filter_by_workspace(entries, config.WORKSPACE_ID)

    sorted_entries = sorted(entries, key=lambda entry: entry["start"])

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
