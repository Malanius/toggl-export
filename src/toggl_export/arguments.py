import argparse
from datetime import date


def validate_start_before_end(start: date, end: date):
    if start > end:
        raise ValueError(f"Start date {start} is after end date {end}")


def init_arguments():
    parser = argparse.ArgumentParser(prog="export", description="Toggl exporter")
    today = date.today()
    parser.add_argument(
        "-s",
        "--start",
        help="Start date (exclusive with --day)",
        required=False,
        type=date.fromisoformat,
    )
    parser.add_argument(
        "-e",
        "--end",
        help="End date (exclusive with --day)",
        required=False,
        type=date.fromisoformat,
    )
    parser.add_argument(
        "-d",
        "--day",
        help="Specific day (exclusive with --start and --end)",
        required=False,
        type=date.fromisoformat,
    )
    parser.add_argument(
        "-c",
        "--client",
        help="Filter by client name",
        required=False,
        default=None,
        type=str,
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

    if args.day and (args.start or args.end):
        raise ValueError("Day argument is exclusive with start and end")

    if args.day:
        args.start = args.end = args.day
    else:
        args.start = args.start or today
        args.end = args.end or today

    validate_start_before_end(args.start, args.end)
    return args
