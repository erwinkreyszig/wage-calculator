from typing import Any

from sqlmodel import select
from sqlmodel.orm.session import Session
from wage_calc.models import Account, AccountSettings
from wage_calc.repositories.common import create_record, delete_record, update_record


def get_account(
    session: Session, username: str | None = None, id: int | None = None
) -> Account:
    """
    Get an account by username or id.

    If both username and id are provided, the query will filter by both.
    """
    if not username and not id:
        raise ValueError("Must provide either username or id to query account.")
    statement = select(Account).join(AccountSettings)
    if username:
        statement = statement.where(Account.username == username)
    if id:
        statement = statement.where(Account.id == id)
    return session.exec(statement).first()


def create_account(session: Session, account: Account, commit: bool = True) -> Account:
    """Helper function for creating an account."""
    account = create_record(session, account, commit=commit)
    return account


def update_account(
    session: Session, account: Account, form_data: dict[str, Any]
) -> Account:
    """Helper function for updating an account."""
    return update_record(session, account, form_data)


def delete_account(session: Session, account: Account, commit: bool = True) -> bool:
    """Helper function for deleting an account."""
    return delete_record(session, account, commit=commit)


def get_account_settings(
    session: Session, username: str | None = None, id: int | None = None
) -> AccountSettings:
    """
    Get account settings by username or id.

    If both username and id are provided, the account record will be queried by both.
    """
    account = get_account(session, username=username, id=id)
    statement = select(AccountSettings).join(Account)
    if username:
        statement = statement.where(Account.username == account.username)
    if id:
        statement = statement.where(Account.id == account.id)
    return session.exec(statement).first()


def create_account_settings(
    session: Session,
    account_id: int,
    account_settings: AccountSettings,
    commit: bool = True,
) -> AccountSettings:
    """Helper function for creating account settings."""
    account_settings.user_id = account_id
    return create_record(session, account_settings, commit=commit)


def update_account_settings(
    session: Session, account_settings: AccountSettings, form_data: dict[str, Any]
) -> AccountSettings:
    """Helper function for updating account settings."""
    return update_record(session, account_settings, form_data)
