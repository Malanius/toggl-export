import sys
from datetime import date, datetime

import pyperclip
import requests
from loguru import logger
from requests.auth import HTTPBasicAuth
from rich.console import Console

import toggl_export.filters as filters
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
    params = {
        "start_date": f"{start_datetime}",
        "end_date": f"{end_datetime}",
        "meta": "true",
    }
    response = requests.get(
        f"{API_BASE_URL}/{TIME_ENTRIES_ENDPOINT}",
        params,
        auth=HTTPBasicAuth(config.TOKEN, "api_token"),
    )
    logger.debug(f"Url: {response.url}")
    if response.ok:
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Response: {response.json()}")
        return response.json()
    else:
        logger.debug(f"Status: {response.status_code}")
        response.raise_for_status()
        raise Exception("Error retrieving time entries!")


def remove_running_entries(entries: list[TimeEntry]) -> list[TimeEntry]:
    return [entry for entry in entries if entry["duration"] > 0]


def convert_to_sod(date: date):
    return datetime.combine(date, datetime.min.time()).isoformat()


def convert_to_eod(date: date):
    return datetime.combine(date, datetime.max.time()).isoformat()


workdays: dict[str, Workday] = {}


def clear_screen():
    print("\033c", end="", flush=True)


def main():
    console = Console(record=True)
    args = init_arguments()
    start = convert_to_sod(args.start)
    end = convert_to_eod(args.end)
    entries = get_time_entries(start, end)

    entries = remove_running_entries(entries)

    if config.WORKSPACE_ID:
        entries = filters.filter_by_workspace(entries, config.WORKSPACE_ID)

    if args.client:
        entries = filters.filter_by_client(entries, args.client)

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

    if args.interactive:
        clear_screen()

    total_time = 0
    for workday in workdays.values():
        console.print(workday.print(args.hide_time).strip())
        total_time += workday.time_worked
        if args.interactive:
            try:
                stripped = console.export_text().strip()
                if args.skip_header:
                    stripped = "\n".join(stripped.split("\n")[1:])
                pyperclip.copy(stripped)
                input()
            except (KeyboardInterrupt, EOFError):
                break
            clear_screen()

    if not args.interactive:
        console.print(f"\n[green bold]Total time worked: {total_time / 3600:.2f}h")


if __name__ == "__main__":
    main()
