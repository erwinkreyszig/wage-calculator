import reflex as rx

from wage_calc.state.main import TimeEntryState


class SpeedDialHorizontal(rx.ComponentState):
    is_open: bool = False

    @rx.event
    def toggle(self):
        self.is_open = not self.is_open

    @classmethod
    def get_component(cls, **props):
        def menu_item(icon: str, text: str, on_click: callable) -> rx.Component:
            return rx.tooltip(
                rx.icon_button(
                    rx.icon(icon, padding="2px"),
                    variant="soft",
                    color_scheme="gray",
                    size="3",
                    cursor="pointer",
                    radius="full",
                    on_click=on_click,
                ),
                side="top",
                content=text,
            )

        def menu() -> rx.Component:
            return rx.hstack(
                menu_item("log_out", "Logout", TimeEntryState.logout),
                menu_item("settings", "Settings", TimeEntryState.logout),
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
                                cls.is_open, "rotate(90deg)", "rotate(0)"
                            ),
                            "transition": "transform 150ms cubic-bezier(0.4, 0, 0.2, 1)",
                        },
                        class_name="dial",
                    ),
                    variant="solid",
                    color_scheme="green",
                    size="3",
                    cursor="pointer",
                    radius="full",
                    position="relative",
                ),
                rx.cond(
                    cls.is_open,
                    menu(),
                ),
                position="relative",
            ),
            on_click=cls.toggle(),
            style={"bottom": "-10px", "right": "5px"},
            position="absolute",
            **props,
        )
