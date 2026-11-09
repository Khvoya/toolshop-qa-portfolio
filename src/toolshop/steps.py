from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import allure

P = ParamSpec("P")
R = TypeVar("R")


def step(title: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            with allure.step(title):
                return function(*args, **kwargs)

        return wrapped

    return decorator
