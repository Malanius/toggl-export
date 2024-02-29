import argparse
from datetime import date


def validate_start_before_end(start: date, end: date):
    if start > end:
        raise ValueError(f"Start date {start} is after end date {end}")


def init_arguments():
    parser = argparse.ArgumentParser(prog="export", description="Toggl exporter")
    today = date.today().isoformat()
    parser.add_argument(
        "-s",
        "--start",
        help="Start date",
        required=False,
        default=today,
        type=date.fromisoformat,
    )
    parser.add_argument(
        "-e",
        "--end",
        help="End date",
        required=False,
        default=today,
        type=date.fromisoformat,
    )
    parser.add_argument(
        "-i",
        "--interactive",
        help="Interactive mode, displays single day at a time",
        required=False,
        default=False,
        action="store_true",
    )
    args = parser.parse_args()
    validate_start_before_end(args.start, args.end)
    return args
