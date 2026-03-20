"""Protected page wrapper for authenticated pages."""

import reflex as rx

from wage_calc.state.auth import AuthState


def protected_page(page_component: rx.Component) -> rx.Component:
    """
    Wrapper that checks authentication and shows content or redirects.

    If user is not logged in, shows a loading screen and redirects to login.

    Args:
        page_component: The page component to protect

    Returns:
        The page if user is logged in, otherwise redirects to login
    """
    return rx.cond(
        AuthState.logged_in,
        page_component,
        rx.center(
            rx.spinner(on_mount=AuthState.check_login),
            width="100%",
            min_height="100vh",
        ),
    )
