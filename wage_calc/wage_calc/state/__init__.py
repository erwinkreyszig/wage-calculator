"""State management for the wage calculator app."""

from wage_calc.state.auth import AuthState
from wage_calc.state.base import State

__all__ = ["State", "AuthState"]
