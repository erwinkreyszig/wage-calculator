import reflex as rx

from wage_calc.state.base import State

user_page_flex_component_args = {
    "width": "100%",
    "min_height": "100vh",
    "justify": "center",
    "align": "center",
}
user_page_vstack_component_args = {
    "width": "100%",
    "max_width": "22rem",
    "padding": "2rem",
    "border_radius": "12px",
    "border": "1px solid",
    "border_color": "gray.8",
    "background": "var(--color-panel)",
    "box_shadow": "medium",
}
flex_component_args = {
    "width": "100%",
    "min_height": "100vh",
    "justify": "center",
    "align": "center",
}
vstack_component_args = {
    "width": "100%",
    "max_width": "22rem",
    "padding": "2rem",
    "border_radius": "12px",
    "border": "1px solid",
    "border_color": "gray.8",
    "background": "var(--color-panel)",
    "box_shadow": "medium",
}
form_vstack_args = {
    "width": "100%",
    "margin_top": "0.1rem",
    "padding": "0.9rem",
    "border_radius": "12px",
    "border": "1px solid",
    "border_color": "gray.7",
    "background": "var(--color-panel)",
}
day_status_vstack_args = {
    "width": "100%",
    "margin_top": "0.75rem",
    "padding": "1.0rem",
    "border_radius": "12px",
    "border": "1px solid",
    "border_color": "gray.7",
    "background": "var(--color-panel)",
}


class SpeedDialHorizontal(rx.ComponentState):
    is_open: bool = False

    @rx.event
    def toggle(self):
        self.is_open = not self.is_open

    @classmethod
    def get_component(self, **props):
        def menu_item(icon: str, text: str, on_click: callable) -> rx.Component:
            return rx.tooltip(
                rx.icon_button(
                    rx.icon(icon, padding="2px"),
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                    cursor="pointer",
                    radius="full",
                    on_click=on_click,
                ),
                side="top",
                content=text,
            )

        def menu() -> rx.Component:
            return rx.hstack(
                menu_item("log_out", "Logout", State.logout),
                # menu_item("settings", "Settings", State.logout),
                rx.match(
                    props.pop("page"),
                    (
                        "records",
                        menu_item("clipboard_pen", "Log", State.go_to_main),
                    ),
                    menu_item("notebook_text", "Records", State.go_to_records),
                ),
                position="absolute",
                bottom="0",
                spacing="2",
                padding_right="10px",
                right="100%",
                direction="row-reverse",
                align_items="center",
            )

        return rx.box(
            rx.box(
                rx.icon_button(
                    rx.icon(
                        "ellipsis_vertical",
                        style={
                            "transform": rx.cond(
                                self.is_open, "rotate(90deg)", "rotate(0)"
                            ),
                            "transition": "transform 150ms cubic-bezier(0.4, 0, 0.2, 1)",
                        },
                        class_name="dial",
                    ),
                    variant="solid",
                    color_scheme="green",
                    size="2",
                    cursor="pointer",
                    radius="full",
                    position="relative",
                ),
                rx.cond(
                    self.is_open,
                    menu(),
                ),
                position="relative",
            ),
            on_click=self.toggle(),
            style={"bottom": "-10px", "right": "5px"},
            position="absolute",
            **props,
        )


def username_and_menu(user_state_var, page_name: str) -> rx.Component:
    speed_dial_horizontal = SpeedDialHorizontal.create

    def speed_dial_menu() -> rx.Component:
        return rx.box(
            speed_dial_horizontal(page=page_name),
            position="relative",
            width="100%",
        )

    return (
        rx.hstack(
            rx.text(
                user_state_var.username,
                size="4",
                weight="medium",
            ),
            rx.spacer(),
            speed_dial_menu(),
            align="center",
            width="100%",
        ),
    )


def error_message_box(form_error_state_var) -> rx.Component:
    return (
        rx.cond(
            form_error_state_var,
            rx.callout(
                form_error_state_var,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
            ),
        ),
    )


def success_message_box(form_message_state_var) -> rx.Component:
    return (
        rx.cond(
            form_message_state_var,
            rx.callout(
                form_message_state_var,
                icon="check",
                color_scheme="green",
                width="100%",
            ),
        ),
    )
