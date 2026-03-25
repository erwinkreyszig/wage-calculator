import logging
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import func, select
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


def set_to_end_of(period: str, date_obj: datetime) -> datetime:
    end_timestamp = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
    if period == "day":
        return end_timestamp
    # TODO: implement period == "month" and period == "year", similar to above
    return end_timestamp


def get_time_record_by_id(session: Session, record_id: int) -> TimeRecord | None:
    statement = select(TimeRecord).where(TimeRecord.id == record_id)
    return session.exec(statement).first()


def get_time_records(
    session: Session,
    user_id: int,
    start_timestamp: datetime | None,
    end_timestamp: datetime | None,
    limit: int | None = None,
    offset: int | None = None,
) -> tuple[list[TimeRecord, int]]:
    """
    Return all time records for a user within the given time range.

    params:
    - session: the database session to use for the query
    - user_id: the primary key of the user whose time records to retrieve
    - start_timestamp: the beginning of the time range to filter by
    - end_timestamp: the end of the time range to filter by

    result: a tuple containing
        the list of TimeRecord objects that match the filtering criteria, and
        the number of matching rows
    """
    in_start_ts_range = (TimeRecord.start_ts >= start_timestamp) & (
        TimeRecord.start_ts <= end_timestamp
    )
    in_end_ts_range = (TimeRecord.end_ts >= start_timestamp) & (
        TimeRecord.end_ts <= end_timestamp
    )
    conditions = (TimeRecord.user_id == user_id) & (in_start_ts_range | in_end_ts_range)
    statement = select(TimeRecord).where(conditions)
    if offset:
        statement = statement.offset(offset)
    if limit:
        statement = statement.limit(limit)
    statement = statement.order_by(TimeRecord.start_ts.asc(), TimeRecord.end_ts.asc())
    time_records = session.exec(statement).all()
    count_statement = select(func.count()).select_from(TimeRecord).where(conditions)
    time_records_count = session.exec(count_statement).one()
    return (time_records, time_records_count)


def get_time_records_between_range(
    session: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    limit: int,
    offset: int,
) -> list[TimeRecord]:
    range_start = set_to_start_of("day", start_date)
    range_end = set_to_end_of("day", end_date)
    return get_time_records(session, user_id, range_start, range_end, limit, offset)


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
    if start_timestamp.month == 12:
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
