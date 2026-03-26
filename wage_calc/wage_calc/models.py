from datetime import datetime
from typing import List, Optional

import reflex as rx
from passlib.context import CryptContext
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship

ROUNDING_OPTIONS = ("down", "up", "nearest")
PASSWORD_CONTEXT = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def fk_to_account_model(cascade: bool = False) -> Field:
    fk = ForeignKey("account.id")
    if cascade:
        fk = ForeignKey("account.id", ondelete="CASCADE")
    return Field(sa_column=Column(Integer, fk, nullable=False))


def back_populate_from_account(field) -> Relationship:
    return Relationship(back_populates=field)


class Account(rx.Model, table=True):
    username: str
    password: str
    email: str

    time_records: Optional[List["TimeRecord"]] = Relationship(back_populates="user")
    rate_histories: Optional[List["RateHistory"]] = Relationship(back_populates="user")
    increment_histories: Optional[List["IncrementHistory"]] = Relationship(
        back_populates="user"
    )
    rounding_histories: Optional[List["RoundingHistory"]] = Relationship(
        back_populates="user"
    )
    settings: Optional["AccountSettings"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )

    @staticmethod
    def hash_password(plain_text: str) -> str:
        return PASSWORD_CONTEXT.hash(plain_text)

    def is_password_valid(self, plain_text: str) -> bool:
        return PASSWORD_CONTEXT.verify(plain_text, self.password)


class AccountSettings(rx.Model, table=True):
    timezone: str
    current_rate: float
    current_increment: int
    current_rounding: str
    break_duration_minutes: Optional[int]

    user_id: int = fk_to_account_model(cascade=True)
    user: Optional["Account"] = back_populate_from_account("settings")


start_time_desc = "The timestamp in UTC of when work began."
end_time_desc = "The timestamp in UTC when the work ended."
total_minutes_desc = "Total number of minutes between start and end timestamps."
atoe_timezone_desc = "Timezone at the time of entry."
atoe_rate_desc = "Rate (per hour) at the time of entry."
atoe_rounding_desc = "Rounding rule (up/down/closest) at the time of entry."
atoe_increment_desc = "Increment value at the time of entry."
atoe_break_duration_desc = "Break duration in minutes at the time of entry."
amount_earned_desc = (
    "Calculated amount based on start and end times, rate, rounding and increment."
)


class TimeRecord(rx.Model, table=True):
    start_ts: Optional[datetime] = Field(description=start_time_desc)
    end_ts: Optional[datetime] = Field(description=end_time_desc)
    total_time_minutes: Optional[int] = Field(description=total_minutes_desc)
    atoe_timezone: str = Field(description=atoe_timezone_desc)
    atoe_rate: float = Field(description=atoe_rate_desc)
    atoe_rounding: str = Field(description=atoe_rounding_desc)
    atoe_increment: int = Field(description=atoe_increment_desc)
    atoe_break_duration_minutes: Optional[int] = Field(
        description=atoe_break_duration_desc
    )
    amount_earned: float = Field(description=amount_earned_desc)

    user_id: int = fk_to_account_model()
    user: Optional["Account"] = back_populate_from_account("time_records")


rate_desc = "Amount earned per 60 minutes."
increment_desc = (
    "The value at which the calculated total time per day will be rounded to."
)
rounding_desc = "Indicates how the total time will be trimmed."


class RateHistory(rx.Model, table=True):
    rate: float = Field(description=rate_desc)
    effective_ts: datetime
    effective_tz: str

    user_id: int = fk_to_account_model()
    user: Optional["Account"] = back_populate_from_account("rate_histories")


class IncrementHistory(rx.Model, table=True):
    increment: int = Field(description=increment_desc)
    effective_ts: datetime
    effective_tz: str

    user_id: int = fk_to_account_model()
    user: Optional["Account"] = back_populate_from_account("increment_histories")


class RoundingHistory(rx.Model, table=True):
    rounding: str = Field(description=rounding_desc)
    effective_ts: datetime
    effective_tz: str

    user_id: int = fk_to_account_model()
    user: Optional["Account"] = back_populate_from_account("rounding_histories")
