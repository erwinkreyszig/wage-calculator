import reflex as rx

from wage_calc.pages.common import (
    error_message_box,
    flex_component_args,
    form_vstack_args,
    username_and_menu,
    vstack_component_args,
)
from wage_calc.pages.protected import protected_page
from wage_calc.state.records import RecordState


def display_row(time_record: dict, index: int) -> rx.Component:
    is_last_row = index == RecordState.rows.length() - 1
    return rx.table.row(
        rx.cond(
            is_last_row,
            rx.fragment(
                rx.table.cell("Totals:"),
                rx.table.cell(""),
                rx.table.cell(""),
                rx.table.cell(time_record["total_hours"]),
                rx.table.cell(time_record["amount_earned"]),
            ),
            rx.fragment(
                rx.table.cell(time_record["day"]),
                rx.table.cell(time_record["start_time"]),
                rx.table.cell(time_record["end_time"]),
                rx.table.cell(time_record["total_hours"]),
                rx.table.cell(time_record["amount_earned"]),
            ),
        )
    )


def show_table_data() -> rx.Component:
    return rx.vstack(
        rx.cond(
            RecordState.show_page_controls,
            rx.center(
                rx.hstack(
                    rx.button(
                        "Prev",
                        size="1",
                        cursor="pointer",
                        on_click=RecordState.previous_page,
                    ),
                    rx.text(
                        "Page ",
                        RecordState.page_number,
                        " of ",
                        RecordState.total_pages,
                    ),
                    rx.button(
                        "Next",
                        size="1",
                        cursor="pointer",
                        on_click=RecordState.next_page,
                    ),
                    justify="center",
                    width="100%",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            RecordState.show_table,
            rx.table.root(
                rx.table.header(
                    rx.table.column_header_cell("Day"),
                    rx.table.column_header_cell("Start time"),
                    rx.table.column_header_cell("End time"),
                    rx.table.column_header_cell("Total hours"),
                    rx.table.column_header_cell("Amount earned"),
                ),
                rx.table.body(rx.foreach(RecordState.rows, display_row)),
                width="100%",
            ),
        ),
        width="100%",
    )


def range_selection_form() -> rx.Component:
    def time_records_range_header() -> rx.Component:
        return rx.text(
            "Time Records",
            size="3",
            weight="medium",
        )

    def start_date_field() -> rx.Component:
        return (
            rx.hstack(
                rx.text("From:", width="40%"),
                rx.input(
                    type="date",
                    width="100%",
                    size="3",
                    value=RecordState.start_date,
                    on_blur=RecordState.get_range_selection_form_error,
                    on_change=RecordState.set_start_date,
                ),
                align="center",
                spacing="2",
            ),
        )

    def end_date_field() -> rx.Component:
        return (
            rx.hstack(
                rx.text("To:", width="40%"),
                rx.input(
                    type="date",
                    width="100%",
                    size="3",
                    value=RecordState.end_date,
                    on_blur=RecordState.get_range_selection_form_error,
                    on_change=RecordState.set_end_date,
                ),
                align="center",
                spacing="2",
            ),
        )

    def show_records_button() -> rx.Component:
        return (
            rx.button(
                "Load",
                width="100%",
                size="3",
                disabled=RecordState.form_disabled,
                on_click=RecordState.on_load_button_click,
            ),
        )

    return (
        rx.box(
            rx.vstack(
                time_records_range_header(),
                start_date_field(),
                end_date_field(),
                show_records_button(),
                spacing="4",
                width="100%",
                align_items="stretch",
            ),
            **form_vstack_args,
        ),
    )


def records_page() -> rx.Component:
    return protected_page(
        rx.box(
            rx.color_mode.button(position="top-right"),
            rx.flex(
                rx.box(
                    rx.vstack(
                        username_and_menu(RecordState.user, "records"),
                        rx.divider(),
                        range_selection_form(),
                        error_message_box(RecordState.form_error),
                        show_table_data(),
                    ),
                    **vstack_component_args,
                ),
                **flex_component_args,
            ),
            width="100%",
        )
    )
