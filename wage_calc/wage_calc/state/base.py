from typing import Optional

import reflex as rx

from wage_calc.models import Account


class State(rx.State):
    user: Optional[Account] = None

    @rx.event
    def logout(self):
        self.reset()
        self.user = None
        return rx.redirect("/login")

    @rx.event
    def check_login(self):
        if not self.logged_in:
            return rx.redirect("/login")

    @rx.event
    def go_to_main(self):
        return rx.redirect("/main")

    @rx.event
    def go_to_records(self):
        return rx.redirect("/records")

    @rx.var
    def logged_in(self) -> bool:
        return self.user is not None
