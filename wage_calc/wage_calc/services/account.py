from typing import Any

import reflex as rx
from wage_calc.models import Account, AccountSettings
from wage_calc.repositories.account import (
    create_account,
    create_account_settings,
    delete_account,
    get_account,
)


def load_relationship(object: Any, relationship_attr: str) -> None:
    _ = getattr(object, relationship_attr)


def get_user(username: str, password: str) -> Account | None:
    with rx.session() as session:
        account = get_account(session, username=username)
        if not account or not account.is_password_valid(password):
            return None
        load_relationship(account, "settings")
        session.expunge(account)
    return account


def create_user(account_dict: dict, account_settings_dict: dict) -> Account:
    with rx.session() as session:
        try:
            account_dict["password"] = Account.hash_password(account_dict["password"])
            account = Account(**account_dict)
            account = create_account(session, account, commit=False)
            session.flush()
            account_settings = AccountSettings(
                **{**account_settings_dict, "user_id": account.id}
            )
            _ = create_account_settings(
                session, account.id, account_settings, commit=False
            )
            session.commit()
            session.refresh(account)
            load_relationship(account, "settings")
            session.expunge(account)
        except Exception as e:
            session.rollback()
            raise e
    return account


def delete_user(account: Account) -> bool:
    with rx.session() as session:
        try:
            return delete_account(session, account)
        except Exception as e:
            session.rollback()
            raise e
