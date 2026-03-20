"""Wage calculator Reflex app."""

import logging
import sys

import reflex as rx

from .pages import index, login_page, main_page
from .state.main import TimeEntryState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

app = rx.App()
app.add_page(index)
app.add_page(login_page, route="/login")
app.add_page(main_page, route="/main", on_load=TimeEntryState.populate_current_day_data)
