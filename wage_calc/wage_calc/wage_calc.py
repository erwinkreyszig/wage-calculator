"""Wage calculator Reflex app."""

import logging
import sys

import reflex as rx

from wage_calc.pages import login_page, main_page, records_page
from wage_calc.state.main import TimeEntryState
from wage_calc.state.records import RecordState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

app = rx.App()
app.add_page(login_page, route="/login")
app.add_page(main_page, route="/main", on_load=TimeEntryState.populate_current_day_data)
app.add_page(records_page, route="/records", on_load=RecordState.reset_page)
