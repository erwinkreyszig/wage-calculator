import reflex as rx

from wage_calc.services.account import get_user
from wage_calc.state.base import State


class AuthState(State):
    username: str = ""
    password: str = ""
    login_error: str = ""
    is_loading: bool = False

    def signup(self):
        pass  # TODO

    @rx.event
    def reset_form(self):
        self.username = ""
        self.password = ""
        self.login_error = ""
        self.is_loading = False

    @rx.event
    def login(self):
        self.login_error = ""
        self.is_loading = True

        if not self.username or not self.password:
            self.login_error = "Username and password are required."
            self.is_loading = False
            return

        account_data = {
            "username": self.username,
            "password": self.password,
        }
        try:
            account = get_user(**account_data)
            if not account:
                self.login_error = "Invalid username or password."
                self.is_loading = False
                return
            self.user = account
            self.reset_form()
            return rx.redirect("/main")
        except Exception as e:
            self.login_error = f"Login error: {str(e)}"
            self.is_loading = False

    @rx.event
    def set_username(self, username: str):
        self.username = username
        self.login_error = ""

    @rx.event
    def set_password(self, password: str):
        self.password = password
        self.login_error = ""

    @rx.event
    def handle_enter_key(self, key: str):
        if key in ("Enter", "Return") and not self.is_loading:
            self.login()

    def redirect_to_main(self):
        if self.logged_in:
            return rx.redirect("/main")
        return None
