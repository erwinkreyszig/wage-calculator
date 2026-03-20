import reflex as rx

from wage_calc.pages.menu import SpeedDialHorizontal
from wage_calc.pages.protected import protected_page
from wage_calc.state.main import TimeEntryState

speed_dial_horizontal = SpeedDialHorizontal.create


def render_horizontal() -> rx.Component:
    return rx.box(
        speed_dial_horizontal(),
        position="relative",
        width="100%",
    )


def main_page() -> rx.Component:
    """Main page where users log/update time records."""
    return protected_page(
        rx.box(
            rx.color_mode.button(position="top-right"),
            rx.flex(
                rx.box(
                    rx.vstack(
                        # Top bar: username + speed dial
                        rx.hstack(
                            rx.text(
                                TimeEntryState.user.username,
                                size="4",
                                weight="medium",
                            ),
                            rx.spacer(),
                            # Menu: logout and settings
                            render_horizontal(),
                            align="center",
                            width="100%",
                        ),
                        # Divider between header and time entry box
                        rx.divider(),
                        # Time entry form box
                        rx.box(
                            rx.vstack(
                                rx.text(
                                    "Time Entry",
                                    size="2",
                                    weight="medium",
                                ),
                                rx.input(
                                    type="date",
                                    width="100%",
                                    size="3",
                                    value=TimeEntryState.date,
                                    on_change=TimeEntryState.set_date,
                                    on_focus=TimeEntryState.on_date_field_focus,
                                    on_blur=TimeEntryState.on_date_field_blur,
                                ),
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
                                rx.button(
                                    "Save",
                                    width="100%",
                                    size="3",
                                    on_click=TimeEntryState.save_time_entry,
                                    is_disabled=TimeEntryState.form_disabled,
                                ),
                                spacing="4",
                                width="100%",
                                align_items="stretch",
                            ),
                            width="100%",
                            margin_top="0.5rem",
                            padding="1.5rem",
                            border_radius="12px",
                            border="1px solid",
                            border_color="gray.7",
                            background="var(--color-panel)",
                        ),
                        # Error message box
                        rx.cond(
                            TimeEntryState.form_error,
                            rx.callout(
                                TimeEntryState.form_error,
                                icon="triangle_alert",
                                color_scheme="red",
                                width="100%",
                            ),
                        ),
                        # Success message box
                        rx.cond(
                            TimeEntryState.generic_message,
                            rx.callout(
                                TimeEntryState.generic_message,
                                icon="check",
                                color_scheme="green",
                                width="100%",
                            ),
                        ),
                        # Day stats box
                        rx.cond(
                            TimeEntryState.show_day_stats,
                            rx.box(
                                rx.vstack(
                                    rx.box(
                                        rx.text(
                                            "Calculations for selected date:", size="2"
                                        ),
                                        rx.text(
                                            TimeEntryState.day_hours,
                                            " hour(s) at ",
                                            TimeEntryState.current_rate,
                                            " per hour: ",
                                            TimeEntryState.day_amount,
                                            size="2",
                                        ),
                                    ),
                                    spacing="2",
                                    width="100%",
                                    align_items="stretch",
                                ),
                                width="100%",
                                margin_top="0.75rem",
                                padding="1.0rem",
                                border_radius="12px",
                                border="1px solid",
                                border_color="gray.7",
                                background="var(--color-panel)",
                            ),
                        ),
                        spacing="2",
                        width="100%",
                        align_items="stretch",
                    ),
                    width="100%",
                    max_width="22rem",
                    padding="2rem",
                    border_radius="12px",
                    border="1px solid",
                    border_color="gray.8",
                    background="var(--color-panel)",
                    box_shadow="medium",
                ),
                width="100%",
                min_height="100vh",
                justify="center",
                align="center",
            ),
            width="100%",
        )
    )
