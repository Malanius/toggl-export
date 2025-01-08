import pytest
import argparse
from datetime import date
from toggl_export.arguments import init_arguments, validate_start_before_end


def test_validate_start_before_end():
    start = date(2023, 1, 1)
    end = date(2023, 1, 2)
    validate_start_before_end(start, end)  # Should not raise an error

    with pytest.raises(ValueError):
        validate_start_before_end(end, start)  # Should raise an error

def test_init_arguments_with_date(mocker):
    mocker.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        date=date(2023, 1, 1), start=None, end=None, client=None, interactive=False))
    args = init_arguments()
    assert args.start == date(2023, 1, 1)
    assert args.end == date(2023, 1, 1)

def test_init_arguments_with_start_and_end(mocker):
    mocker.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        date=None, start=date(2023, 1, 1), end=date(2023, 1, 2), client=None, interactive=False))
    args = init_arguments()
    assert args.start == date(2023, 1, 1)
    assert args.end == date(2023, 1, 2)

def test_init_arguments_with_defaults(mocker):
    today = date.today()
    mocker.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        date=None, start=None, end=None, client=None, interactive=False))
    args = init_arguments()
    assert args.start == today
    assert args.end == today

def test_init_arguments_exclusive_date_and_start_end(mocker):
    mocker.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        date=date(2023, 1, 1), start=date(2023, 1, 1), end=None, client=None, interactive=False))
    with pytest.raises(ValueError):
        init_arguments()
