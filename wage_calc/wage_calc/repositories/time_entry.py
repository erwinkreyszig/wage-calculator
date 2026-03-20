import logging
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import select
from sqlmodel.orm.session import Session
from wage_calc.models import TimeRecord
from wage_calc.repositories.common import create_record, update_record

logger = logging.getLogger(__name__)


def create_time_record(session: Session, record: TimeRecord) -> TimeRecord:
    """Helper function for creating a time record."""
    return create_record(session, record)


def update_time_record(
    session: Session, record: TimeRecord, form_data: dict[str, Any]
) -> TimeRecord:
    """Helper function for updating a time record."""
    return update_record(session, record, form_data)


def set_to_start_of(period: str, date_obj: datetime) -> datetime:
    """
    Helper function to set the date object at the beginning of
    the day, month, or year.
    """
    start_timestamp = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "day":
        return start_timestamp
    if period in ("month", "year"):
        start_timestamp = start_timestamp.replace(day=1)
    if period == "year":
        start_timestamp = start_timestamp.replace(month=1)
    return start_timestamp


def get_time_record_by_id(session: Session, record_id: int) -> TimeRecord | None:
    statement = select(TimeRecord).where(TimeRecord.id == record_id)
    return session.exec(statement).first()


def get_time_records(
    session: Session,
    user_id: int,
    start_timestamp: datetime | None,
    end_timestamp: datetime | None,
) -> list[TimeRecord]:
    """
    Return all time records for a user within the given time range.

    params:
    - session: the database session to use for the query
    - user_id: the primary key of the user whose time records to retrieve
    - start_timestamp: the beginning of the time range to filter by
    - end_timestamp: the end of the time range to filter by

    result: a list of TimeRecord objects that match the filtering criteria
    """
    statement = select(TimeRecord).where(TimeRecord.user_id == user_id)
    in_start_ts_range = (TimeRecord.start_ts >= start_timestamp) & (
        TimeRecord.start_ts <= end_timestamp
    )
    in_end_ts_range = (TimeRecord.end_ts >= start_timestamp) & (
        TimeRecord.end_ts <= end_timestamp
    )
    statement = statement.where(in_start_ts_range | in_end_ts_range).order_by(
        TimeRecord.start_ts
    )
    return session.exec(statement).all()


def get_time_records_for_day(
    session: Session, user_id: int, date_obj: datetime
) -> TimeRecord:
    """
    Return the time record for a user for the given calendar day.
    """
    range_start = set_to_start_of("day", date_obj)
    range_end = range_start + timedelta(days=1) - timedelta(microseconds=1)
    return get_time_records(session, user_id, range_start, range_end)


def get_time_records_for_month(
    session: Session, user_id: int, date_obj: datetime
) -> list[TimeRecord]:
    """
    Return all time records for a user for the given calendar month.

    The provided ``date_obj`` can be any ``datetime`` within the target month.
    We compute:
    - ``start_timestamp`` as the first day of that month at 00:00:00.000000
    - ``end_timestamp`` as 1 microsecond before the first day of the next month
    """
    start_timestamp = set_to_start_of("month", date_obj)
    if start_timestamp.date_obj == 12:
        next_month = start_timestamp.replace(
            year=start_timestamp.year + 1, month=1, day=1
        )
    else:
        next_month = start_timestamp.replace(month=start_timestamp.month + 1, day=1)

    end_timestamp = next_month - timedelta(microseconds=1)
    return get_time_records(session, user_id, start_timestamp, end_timestamp)


def get_time_records_for_year(
    session: Session, user_id: int, date_obj: datetime
) -> list[TimeRecord]:
    """Return all time records for a user for the given calendar year.

    The provided ``date_obj`` can be any ``datetime`` within the target year.
    We compute:
    - ``start_timestamp`` as Jan 1 of that year at 00:00:00.000000
    - ``end_timestamp`` as 1 microsecond before Jan 1 of the following year
    """
    start_timestamp = set_to_start_of("year", date_obj)
    next_year = start_timestamp.replace(year=start_timestamp.year + 1)
    end_timestamp = next_year - timedelta(microseconds=1)
    return get_time_records(session, user_id, start_timestamp, end_timestamp)


def calculate_earned_amount(time_record: TimeRecord) -> dict:
    """
    Returns the values for the ``total_time_minutes`` and ``amount_earned``
    using the values for the start and end timestamps, increment, rounding and
    hourly rate values
    """
    total_seconds = (time_record.end_ts - time_record.start_ts).total_seconds()
    total_minutes = total_seconds // 60
    if time_record.atoe_break_duration_minutes:
        total_minutes -= time_record.atoe_break_duration_minutes
    rounded_minutes = get_rounded_value(
        total_minutes, time_record.atoe_rounding, time_record.atoe_increment
    )
    total_hours = rounded_minutes / 60.0
    return {
        "total_time_minutes": total_seconds // 60,
        "amount_earned": total_hours * time_record.atoe_rate,
    }


def save_amount_earned(
    session: Session, time_record: TimeRecord, form_data: dict
) -> TimeRecord:
    """Helper function to calculate and save the amount earned for a time record."""
    form_data = calculate_earned_amount(time_record)
    return update_time_record(session, time_record, form_data)
