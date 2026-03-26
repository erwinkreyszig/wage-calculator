from typing import Any

from sqlmodel.orm.session import Session


def update_record(session: Session, record: Any, form_data: dict[str, Any]) -> Any:
    for key, value in form_data.items():
        setattr(record, key, value)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def create_record(session: Session, record: Any, commit: bool = True) -> Any:
    session.add(record)
    if commit:
        session.commit()
        session.refresh(record)
    return record


def delete_record(session: Session, record: Any, commit: bool = True) -> bool:
    try:
        session.delete(record)
        if commit:
            session.commit()
    except Exception:
        session.rollback()
        return False
    return True
