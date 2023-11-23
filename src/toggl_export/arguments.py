import argparse
from datetime import date, datetime


def validate_date(date):
    try:
        datetime.fromisoformat(date)
    except ValueError:
        raise ValueError(f"Invalid date: {date}")


def validate_start_before_end(start, end):
    start_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)
    if start_date > end_date:
        raise ValueError(f"Start date {start} is after end date {end}")


def validate_dates(start, end):
    validate_date(start)
    validate_date(end)
    validate_start_before_end(start, end)


def init_arguments():
    parser = argparse.ArgumentParser(prog="export", description="Toggl exporter")
    today = date.today().isoformat()
    parser.add_argument(
        "-s", "--start", help="Start date", required=False, default=today
    )
    parser.add_argument("-e", "--end", help="End date", required=False, default=today)
    args = parser.parse_args()
    validate_dates(args.start, args.end)
    return args
