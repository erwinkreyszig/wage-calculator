import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import reflex as rx

from wage_calc.models import TimeRecord
from wage_calc.services.time_entry import (
    create_time_entry,
    get_data_by_record_id,
    get_data_for_date,
    get_rounded_value,
    get_totals_for_month,
    update_time_entry,
)
from wage_calc.state.base import State

logger = logging.getLogger(__name__)
NO_TIME_RECORD = -1


class TimeEntryState(State):
    date: str = ""
    start_time: str = ""
    end_time: str = ""
    show_stats: bool = False
    show_day_stats: bool = False
    show_month_stats: bool = False
    day_hours: float = 0.0
    current_rate: float = 0.0
    day_amount: float = 0.0
    month_hours: float = 0.0
    month_amount: float = 0.0
    form_error: str = ""
    form_disabled: bool = False
    generic_message: str = ""
    _time_record_id: int = NO_TIME_RECORD
    _previous_date: str = ""
    _previous_start_time: str = ""
    _previous_end_time: str = ""

    @rx.var
    def time_record_id(self) -> int:
        return self._time_record_id

    @rx.event
    def set_date(self, date_str: str):
        self.date = date_str

    @rx.event
    def set_start_time(self, start_time: str):
        self.start_time = start_time

    @rx.event
    def set_end_time(self, end_time: str):
        self.end_time = end_time

    @rx.event
    def set_time_record_id(self, record_id: int):
        self._time_record_id = record_id

    @rx.event
    def set_form_error(self, error_message: str):
        self.form_error = error_message
        self.generic_message = ""

    @rx.event
    def populate_current_day_data(self):
        self.clear_form()
        self.set_users_current_day()
        self.handle_date_change()

    def set_users_current_day(self):
        if not self.user:
            return
        now_local = datetime.now(ZoneInfo(self.user.settings.timezone))
        logger.info(f"User's current local datetime: {now_local}")
        self.set_date(now_local.strftime("%Y-%m-%d"))

    @rx.event
    def clear_form(self):
        self.set_start_time("")
        self.set_end_time("")
        self.set_form_error("")
        self.form_disabled = False
        self.generic_message = ""

    @rx.event
    def handle_date_change(self):
        logger.info(f"Handling date change for (local) date: {self.date}")
        if not self.date:
            self.show_stats = False
            self.show_day_stats = False
            self.show_month_stats = False
            return
        date_local = self.__get_date_local()
        time_records_for_date = get_data_for_date(self.user, date_local)
        logger.info(f"Time records for date: {time_records_for_date}")
        if len(time_records_for_date) > 0:
            first_time_record = time_records_for_date[0]
            self.set_time_record_id(first_time_record.id)
            if first_time_record.start_ts:
                localized_start_ts = self.__localize_to_user_timezone(
                    first_time_record.start_ts
                )
                self.set_start_time(localized_start_ts.strftime("%H:%M"))
            if first_time_record.end_ts:
                localized_end_ts = self.__localize_to_user_timezone(
                    first_time_record.end_ts
                )
                self.set_end_time(localized_end_ts.strftime("%H:%M"))
            self.populate_stats(first_time_record)
        else:
            self.set_time_record_id(NO_TIME_RECORD)
            self.set_start_time("")
            self.set_end_time("")
            self.populate_stats()

    @rx.event
    def populate_stats(self, time_record: TimeRecord | None = None):
        # if self._time_record_id == NO_TIME_RECORD:
        #     self.show_stats = False
        #     self.show_day_stats = False
        #     self.show_month_stats = False
        #     return
        # if not time_record:
        #     time_record = get_data_by_record_id(self._time_record_id)
        # if not time_record or (time_record and not time_record.total_time_minutes):
        #     self.show_day_stats = False
        #     return
        # self.day_hours = round(time_record.total_time_minutes / 60.0, 2)
        # self.day_amount = round(time_record.amount_earned, 2)
        # self.current_rate = self.user.settings.current_rate
        # self.show_day_stats = True
        self.set_day_stat_values(time_record)
        self.set_month_stat_values()
        self.show_stats = self.show_day_stats or self.show_month_stats

    @rx.event
    def set_day_stat_values(self, time_record: TimeRecord | None = None):
        if self._time_record_id == NO_TIME_RECORD:
            self.show_day_stats = False
            return
        if not time_record:
            time_record = get_data_by_record_id(self._time_record_id)
        if not time_record or (time_record and not time_record.total_time_minutes):
            self.show_day_stats = False
            return
        self.day_hours = round(time_record.total_time_minutes / 60.0, 2)
        self.day_amount = round(time_record.amount_earned, 2)
        self.current_rate = self.user.settings.current_rate
        self.show_day_stats = True

    @rx.event
    def set_month_stat_values(self):
        date_local = self.__get_date_local()
        month_totals = get_totals_for_month(self.user, date_local)
        if month_totals["num_days"] == 0:
            self.show_month_stats = False
            return
        self.month_hours = month_totals["total_hours"]
        self.month_amount = month_totals["total_amount"]
        self.show_month_stats = True

    @rx.event
    def on_date_field_focus(self):
        self._previous_date = self.date

    @rx.event
    def on_start_time_focus(self):
        self._previous_start_time = self.start_time

    @rx.event
    def on_end_time_focus(self):
        self._previous_end_time = self.end_time

    @rx.event
    def on_date_field_blur(self, value: str):
        logging.info(
            f"Date field blurred with value: {value}, previous value: {self._previous_date}"
        )
        if value == self._previous_date:
            return
        self.clear_form()
        self.handle_date_change()

    @rx.event
    def save_time_entry(self):
        logger.info("Saving time entry...")
        self.form_disabled = True
        self.get_time_entry_form_error()
        if self.form_error:
            return
        if self.time_record_id == NO_TIME_RECORD:
            form_data = {"amount_earned": 0.0}
            if self.start_time:
                form_data["start_ts"] = self.__handle_entered_time("start")
            if self.end_time:
                form_data["end_ts"] = self.__handle_entered_time("end")
            form_data = self.__perform_amount_calculations(form_data)
            form_data.update(
                {
                    "atoe_timezone": self.user.settings.timezone,
                    "atoe_rate": self.user.settings.current_rate,
                    "atoe_rounding": self.user.settings.current_rounding,
                    "atoe_increment": self.user.settings.current_increment,
                    "atoe_break_duration_minutes": self.user.settings.break_duration_minutes,
                }
            )
            logger.info(f"Form data: {form_data}")
            time_record = create_time_entry(self.user, form_data)
            self.set_time_record_id(time_record.id)
            self.generic_message = "Time entry saved."
            logger.info("Time entry created.")
        else:
            if self.__is_removing_value("start") or self.__is_removing_value("end"):
                self.set_form_error("Cannot remove a time")
                self.form_disabled = True
                return
            logger.info(f"TimeRecord id: {self._time_record_id}")
            time_record = get_data_by_record_id(self.time_record_id)
            form_data = {}
            if self.start_time:
                form_data["start_ts"] = self.__handle_entered_time("start")
            if self.end_time:
                form_data["end_ts"] = self.__handle_entered_time("end")
            form_data = self.__perform_amount_calculations(form_data)
            logger.info(f"Form data for update: {form_data}")
            time_record = update_time_entry(time_record, form_data)
            self.generic_message = "Time entry updated."
            logger.info("Time entry updated.")
        self.form_disabled = False
        self.populate_stats()

    def __handle_entered_time(self, field: str):
        logging.info(f"Handling entered {field} time...")
        local_dt = self.__merge_date_and_time(self.date, getattr(self, f"{field}_time"))
        logging.info(f"{field.capitalize()} time (local): {local_dt}")
        if field == "end":
            local_dt = self.__do_time_rounding(local_dt)
            logging.info(f"Rounded {field} time (local): {local_dt}")
        return local_dt

    def __merge_date_and_time(
        self, date_str: str, time_str: str | None = None
    ) -> datetime:
        if not time_str:
            time_str = "00:00"
        naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        local_tz = ZoneInfo(self.user.settings.timezone)
        local_dt = naive_dt.replace(tzinfo=local_tz)
        return local_dt

    def __get_date_local(self):
        return datetime.strptime(self.date, "%Y-%m-%d").replace(
            tzinfo=ZoneInfo(self.user.settings.timezone)
        )

    def __do_time_rounding(self, dt_obj: datetime) -> datetime:
        rounded_minutes = get_rounded_value(
            dt_obj.minute,
            self.user.settings.current_rounding,
            self.user.settings.current_increment,
        )
        if rounded_minutes == 60:
            dt_obj = dt_obj.replace(minute=0) + timedelta(hours=1)
        else:
            dt_obj = dt_obj.replace(minute=rounded_minutes)
        return dt_obj

    def __perform_amount_calculations(self, form_data: dict) -> dict:
        if not form_data.get("start_ts") or not form_data.get("end_ts"):
            logger.info("Start or end time missing, skipping amount calculations.")
            return form_data
        logger.info("Performing amount calculations...")
        total_minutes = self.__calculate_total_minutes(
            form_data["start_ts"],
            form_data["end_ts"],
            self.user.settings.break_duration_minutes,
        )
        amount_earned = self.__calculate_amount_earned(total_minutes)
        logger.info(f"Total minutes: {total_minutes}")
        logger.info(f"Amount earned: {amount_earned}")
        return {
            **form_data,
            "total_time_minutes": total_minutes,
            "amount_earned": amount_earned,
        }

    def __calculate_total_minutes(
        self, start_ts: datetime, end_ts: datetime, break_duration: int
    ) -> int:
        total_seconds = (end_ts - start_ts).total_seconds()
        total_minutes = total_seconds // 60
        return total_minutes - break_duration

    def __calculate_amount_earned(self, total_minutes: int) -> float:
        total_hours = total_minutes / 60.0
        return total_hours * self.user.settings.current_rate

    @rx.event
    def get_time_entry_form_error(self) -> str:
        form_error = ""
        if not self.date:
            form_error = "Date is required."
        elif not self.start_time:
            form_error = "At a minimum, start time is required."
        elif self.start_time and self.end_time:
            if self.start_time == self.end_time:
                form_error = "Start and end times cannot be the same."
            else:
                start_dt = self.__merge_date_and_time(self.date, self.start_time)
                end_dt = self.__merge_date_and_time(self.date, self.end_time)
                if start_dt >= end_dt:
                    form_error = "Start time must be before end time."
        elif self.start_time and not self.__is_time_valid(self.start_time):
            form_error = "Entered start time is not valid."
        elif self.end_time and not self.__is_time_valid(self.end_time):
            form_error = "Entered end time is not valid."
        self.set_form_error(form_error)
        self.form_disabled = form_error != ""
        if form_error != "":
            self.handle_date_change()

    def __is_time_valid(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def __localize_to_user_timezone(self, dt_obj: datetime) -> datetime:
        return dt_obj.astimezone(ZoneInfo(self.user.settings.timezone))

    def __is_removing_value(self, start_or_end: str) -> bool:
        previous_value = getattr(self, f"_previous_{start_or_end}_time")
        new_value = getattr(self, f"{start_or_end}_time")
        return previous_value != "" and new_value == ""

    @rx.event
    def go_to_records_page(self):
        rx.redirect("/records")
