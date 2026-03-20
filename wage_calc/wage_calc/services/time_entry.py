from datetime import datetime

import reflex as rx
from wage_calc.models import Account, TimeRecord
from wage_calc.repositories.time_entry import (
    create_time_record,
    get_time_record_by_id,
    get_time_records_for_day,
    update_time_record,
)


def get_data_for_date(user: Account, date_obj: datetime) -> list[TimeRecord]:
    with rx.session() as session:
        time_records = get_time_records_for_day(session, user.id, date_obj)
    return time_records


def get_data_by_record_id(record_id: int) -> TimeRecord | None:
    time_record = None
    with rx.session() as session:
        time_record = get_time_record_by_id(session, record_id)
        if time_record:
            session.expunge(time_record)
    return time_record


def get_rounded_value(value: int, method: str, increment: int) -> int:
    """
    Round an integer value to the nearest increment using the given method.

    Args:
        value: The integer value to be rounded.
        method: One of ``\"up\"``, ``\"down\"``, or ``\"closest\"``.
        increment: The step size to round to (must be > 0).

    Behavior examples:
        - 12, \"up\", 5      -> 15
        - 12, \"down\", 5    -> 10
        - 12, \"closest\", 5 -> 10
        - 17, \"up\", 10     -> 20
        - 17, \"down\", 10   -> 10
        - 17, \"closest\", 10-> 20

    For ``method == \"closest\"``, values strictly between the lower and upper
    bounds are rounded to the upper bound (ties are also rounded up).
    """
    if increment <= 0:
        raise ValueError("Increment must be a positive integer.")

    if method not in {"up", "down", "closest"}:
        raise ValueError(f"Unsupported rounding method: {method!r}.")

    # Already aligned to the increment.
    if value % increment == 0:
        return value

    lower = (value // increment) * increment
    upper = lower + increment

    if method == "down":
        return lower
    if method == "up":
        return upper

    # method == "closest"
    distance_to_lower = value - lower
    distance_to_upper = upper - value

    # On tie or closer to upper, choose upper (round up).
    if distance_to_upper <= distance_to_lower:
        return upper
    return lower


def create_time_entry(user: Account, form_data: dict) -> TimeRecord:
    time_record = TimeRecord(**{**form_data, "user_id": user.id})
    with rx.session() as session:
        try:
            time_record = create_time_record(session, time_record)
            session.commit()
            session.refresh(time_record)
            session.expunge(time_record)
        except Exception as e:
            session.rollback()
            raise e
    return time_record


def update_time_entry(time_record: TimeRecord, form_data: dict) -> TimeRecord:
    with rx.session() as session:
        try:
            updated_time_record = update_time_record(session, time_record, form_data)
            session.commit()
            session.refresh(updated_time_record)
        except Exception as e:
            session.rollback()
            raise e
    return updated_time_record
