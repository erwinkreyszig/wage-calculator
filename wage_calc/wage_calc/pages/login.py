"""Login page."""

import reflex as rx

from wage_calc.state.auth import AuthState


def login_page() -> rx.Component:
    """Login page: centered box with username, password, keep logged in, links, and button."""
    login_form = rx.box(
        rx.color_mode.button(position="top-right"),
        rx.flex(
            rx.box(
                rx.vstack(
                    rx.heading("Log in", size="6", margin_bottom="4"),
                    rx.cond(
                        AuthState.login_error,
                        rx.callout(
                            AuthState.login_error,
                            icon="triangle_alert",
                            color_scheme="red",
                            width="100%",
                        ),
                    ),
                    rx.input(
                        placeholder="Username",
                        value=AuthState.username,
                        on_change=AuthState.set_username,
                        on_key_down=AuthState.handle_enter_key,
                        width="100%",
                        size="3",
                    ),
                    rx.input(
                        placeholder="Password",
                        type="password",
                        value=AuthState.password,
                        on_change=AuthState.set_password,
                        on_key_down=AuthState.handle_enter_key,
                        width="100%",
                        size="3",
                    ),
                    # rx.checkbox(
                    #     "Keep me logged in",
                    #     checked=AuthState.keep_logged_in,
                    #     on_change=AuthState.set_keep_logged_in,
                    #     size="2",
                    # ),
                    rx.button(
                        rx.cond(AuthState.is_loading, "Logging in...", "Log in"),
                        on_click=AuthState.login,
                        width="100%",
                        size="3",
                        is_disabled=AuthState.is_loading,
                    ),
                    rx.hstack(
                        rx.link("Forgot password?", href="/forgot-password", size="2"),
                        rx.text(" · ", size="2"),
                        rx.link("Create account", href="/signup", size="2"),
                        spacing="2",
                        wrap="wrap",
                    ),
                    spacing="6",
                    width="100%",
                    align_items="stretch",
                ),
                width="100%",
                max_width="22rem",
                padding="1.5rem",
                border_radius="9px",
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

    # If user is already logged in, redirect to main page
    return rx.cond(
        AuthState.logged_in,
        rx.box(on_mount=AuthState.redirect_to_main),
        login_form,
    )
