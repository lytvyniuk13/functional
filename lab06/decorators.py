"""decorators.py — Параметризовані декоратори як функції вищого порядку (HOF).

Містить @validate, @timed та @logged з ін'єкцією залежностей і збереженням метаданих.
"""

from __future__ import annotations
import functools
import inspect
import time
from typing import Any, Callable, Literal, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def validate(
    **validators: Callable[[Any], None],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Параметризований декоратор валідації аргументів (Варіант №9).

    Зв'язує позиційні та іменовані параметри через inspect.signature(func).bind
    і викликає відповідні валідатори до початку виконання цільової функції.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, validator_fn in validators.items():
                if param_name in bound.arguments:
                    validator_fn(bound.arguments[param_name])

            return func(*args, **kwargs)

        return wrapper

    return decorator


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Параметризований декоратор вимірювання часу виконання.

    Використовує блок finally для гарантованого логування навіть при винятку.
    Ін'єкція clock та logger уможливлює швидке та детерміноване тестування.
    """
    scale = {"s": 1.0, "ms": 1e3, "us": 1e6}[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        op_name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = clock()
            try:
                return func(*args, **kwargs)
            finally:
                dt = (clock() - t0) * scale
                logger(f"[timed] {op_name} took {dt:.3f} {unit}")

        return wrapper

    return decorator


def logged(
    prefix: str = "APP",
    *,
    logger: Callable[[str], None] = print,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Параметризований декоратор логування викликів, параметрів, значень та помилок."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            logger(
                f"[{prefix}] Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            try:
                result = func(*args, **kwargs)
                logger(f"[{prefix}] {func.__name__} returned {result}")
                return result
            except Exception as exc:
                logger(f"[{prefix}] {func.__name__} raised {exc!r}")
                raise

        return wrapper

    return decorator