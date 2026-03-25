import reflex as rx

from wage_calc.pages.common import (
    day_status_vstack_args,
    error_message_box,
    flex_component_args,
    form_vstack_args,
    success_message_box,
    username_and_menu,
    vstack_component_args,
)
from wage_calc.pages.protected import protected_page
from wage_calc.state.main import TimeEntryState


def time_entry_form() -> rx.Component:
    def time_entry_form_header() -> rx.Component:
        return (
            rx.text(
                "Time Entry",
                size="3",
                weight="medium",
            ),
        )

    def date_field() -> rx.Component:
        return (
            rx.hstack(
                rx.text("Date:", width="50%"),
                rx.input(
                    type="date",
                    width="100%",
                    size="3",
                    value=TimeEntryState.date,
                    on_change=TimeEntryState.set_date,
                    on_focus=TimeEntryState.on_date_field_focus,
                    on_blur=TimeEntryState.on_date_field_blur,
                ),
                align="center",
                spacing="2",
            ),
        )

    def start_time_field() -> rx.Component:
        return (
            rx.hstack(
                rx.text("Start time:", width="50%"),
                rx.input(
                    placeholder="Start time",
                    type="time",
                    step=60,
                    width="100%",
                    size="3",
                    value=TimeEntryState.start_time,
                    on_change=TimeEntryState.set_start_time,
                    on_focus=TimeEntryState.on_start_time_focus,
                    on_blur=TimeEntryState.get_time_entry_form_error,
                ),
                align="center",
                spacing="2",
            ),
        )

    def end_time_field() -> rx.Component:
        return (
            rx.hstack(
                rx.text("End time:", width="50%"),
                rx.input(
                    placeholder="End time",
                    type="time",
                    step=60,
                    width="100%",
                    size="3",
                    value=TimeEntryState.end_time,
                    on_change=TimeEntryState.set_end_time,
                    on_focus=TimeEntryState.on_end_time_focus,
                    on_blur=TimeEntryState.get_time_entry_form_error,
                ),
                align="center",
                spacing="2",
            ),
        )

    def save_button() -> rx.Component:
        return (
            rx.button(
                "Save",
                width="100%",
                size="3",
                disabled=TimeEntryState.form_disabled,
                on_click=TimeEntryState.save_time_entry,
            ),
        )

    return (
        rx.box(
            rx.vstack(
                time_entry_form_header(),
                date_field(),
                start_time_field(),
                end_time_field(),
                save_button(),
                spacing="4",
                width="100%",
                align_items="stretch",
            ),
            **form_vstack_args,
        ),
    )


def selected_date_stats() -> rx.Component:
    def day_stats_box() -> rx.Component:
        return rx.cond(
            TimeEntryState.show_day_stats,
            rx.box(
                rx.text("Calculations for selected date:", size="2"),
                rx.text(
                    TimeEntryState.day_hours,
                    " hour(s) at ",
                    TimeEntryState.current_rate,
                    " per hour: ",
                    TimeEntryState.day_amount,
                    size="2",
                ),
            ),
        )

    def month_stats_box() -> rx.Component:
        return rx.cond(
            TimeEntryState.show_month_stats,
            rx.box(
                rx.text("Selected month totals:", size="2"),
                rx.text(
                    TimeEntryState.month_hours,
                    " hour(s), amount is: ",
                    TimeEntryState.month_amount,
                    size="2",
                ),
            ),
        )

    return (
        rx.cond(
            TimeEntryState.show_stats,
            rx.box(
                rx.vstack(
                    day_stats_box(),
                    month_stats_box(),
                    spacing="2",
                    width="100%",
                    align_items="stretch",
                ),
                **day_status_vstack_args,
            ),
        ),
    )


def main_page() -> rx.Component:
    """Main page where users log/update time records."""
    return protected_page(
        rx.box(
            rx.color_mode.button(position="top-right"),
            rx.flex(
                rx.box(
                    rx.vstack(
                        username_and_menu(TimeEntryState.user, "main"),
                        rx.divider(),
                        time_entry_form(),
                        error_message_box(TimeEntryState.form_error),
                        success_message_box(TimeEntryState.generic_message),
                        selected_date_stats(),
                        spacing="2",
                        width="100%",
                        align_items="stretch",
                    ),
                    **vstack_component_args,
                ),
                **flex_component_args,
            ),
            width="100%",
        )
    )
