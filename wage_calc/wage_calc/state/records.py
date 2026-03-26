import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import reflex as rx

from wage_calc.models import TimeRecord
from wage_calc.services.time_entry import get_time_entry_records
from wage_calc.state.base import State

logger = logging.getLogger(__name__)


class RecordState(State):
    start_date: str = ""
    end_date: str = ""
    form_error: str = ""
    form_disabled: bool = False
    show_page_controls: bool = False
    page_control_info: str = ""
    offset: int = 0
    limit: int = 15
    rows: list[dict] = []
    total_rows: int
    show_table: bool = False

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1 + (1 if self.offset % self.limit else 0)

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return (self.total_rows // self.limit) + (
            1 if self.total_rows % self.limit else 0
        )

    @rx.event
    def previous_page(self):
        self.offset = max(self.offset - self.limit, 0)
        self.get_time_records()

    @rx.event
    def next_page(self):
        if self.offset + self.limit < self.total_rows:
            self.offset += self.limit
        self.get_time_records()

    def _get_total_items(self):
        pass
        # self.total_items =

    @rx.event
    def set_start_date(self, value: str):
        self.start_date = value

    @rx.event
    def set_end_date(self, value: str):
        self.end_date = value

    @rx.event
    def set_form_error(self, value: str):
        self.form_error = value

    @rx.event
    def go_to_main_page(self):
        return rx.redirect("/main")

    @rx.event
    def reset_page(self):
        self.start_date = ""
        self.end_date = ""
        self.form_disabled = False
        self.show_page_controls = False
        self.show_table = False
        self.rows = []

    @rx.event
    def get_range_selection_form_error(self):
        form_error = ""
        if not self.start_date and not self.end_date:
            form_error = "Both start and end date are required."
        elif not self.start_date:
            form_error = "Start date is missing."
        elif not self.end_date:
            form_error = "End date is missing."
        elif self.start_date == self.end_date:
            form_error = "Start and end dates cannot be the same."
        else:
            start_dt = self.__get_date_object(self.start_date)
            end_dt = self.__get_date_object(self.end_date)
            if start_dt > end_dt:
                form_error = "End date cannot be before start date."
        self.set_form_error(form_error)
        self.form_disabled = form_error != ""

    def __get_date_object(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d")

    @rx.event
    def on_load_button_click(self):
        self.offset = 0
        self.get_time_records()

    @rx.event
    def get_time_records(self):
        logging.info(
            f"Fetching records from {self.start_date} to {self.end_date}, inclusive of dates mentioned. "
            f"offset: {self.offset}, limit: {self.limit}"
        )
        rows, self.total_rows = get_time_entry_records(
            self.user,
            self.__get_date_object(self.start_date),
            self.__get_date_object(self.end_date),
            self.limit,
            self.offset,
        )
        self.rows = self.__format_row_values(rows)
        self.show_page_controls = False
        self.page_control_info = ""
        if self.total_rows > self.limit:
            self.show_page_controls = True
            self.page_control_info = ""
        self.show_table = False
        if self.total_rows > 0:
            self.show_table = True

    def __format_row_values(self, time_records: list[TimeRecord]) -> list[dict]:
        formatted = []
        sum_minutes = 0
        sum_amount = 0
        for row in time_records:
            day_local = ""
            ts_ref = row.start_ts or row.end_ts
            day_local = self.__localize(ts_ref, self.user.settings.timezone).strftime(
                "%b %d"
            )
            start_time_local = ""
            if row.start_ts:
                start_time_local = self.__localize(
                    row.start_ts, self.user.settings.timezone
                ).strftime("%H:%M")
            end_time_local = ""
            if row.end_ts:
                end_time_local = self.__localize(
                    row.end_ts, self.user.settings.timezone
                ).strftime("%H:%M")
            total_hours = 0.0
            if row.total_time_minutes:
                total_hours = round(row.total_time_minutes / 60.0, 1)
                sum_minutes += row.total_time_minutes
            amount_earned = 0.0
            if row.amount_earned:
                amount_earned = round(row.amount_earned, 1)
                sum_amount += row.amount_earned
            formatted.append(
                {
                    "day": day_local,
                    "start_time": start_time_local,
                    "end_time": end_time_local,
                    "total_hours": total_hours,
                    "amount_earned": amount_earned,
                    "ts_ref": ts_ref,
                }
            )
        totals_row = {
            "day": "",
            "start_time": "",
            "end_time": "",
            "total_hours": round(sum_minutes / 60, 1),
            "amount_earned": round(sum_amount, 1),
        }
        return [*sorted(formatted, key=lambda x: x["ts_ref"]), totals_row]

    def __localize(self, utc_ts: datetime, timezone_str: str) -> datetime:
        tz = ZoneInfo(timezone_str)
        return utc_ts.astimezone(tz)
