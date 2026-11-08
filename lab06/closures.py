"""closures.py — Фабрики замикань (Closures) для Варіанта №9.

Демонструє захоплення та утримання стану (stateful closure via nonlocal)
і параметризовані фабрики валідаторів аргументів.
"""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def make_counter(start: int = 0) -> Callable[[], int]:
    """Замикання зі змінним внутрішнім станом (Stateful Closure).

    Використовує ключове слово nonlocal для модифікації захопленої змінної value.
    """
    value = start

    def increment() -> int:
        nonlocal value
        value += 1
        return value

    return increment


def make_range_validator(
    min_val: float | None = None,
    max_val: float | None = None,
    arg_name: str = "arg",
) -> Callable[[Any], None]:
    """Фабрика валідаторів числового діапазону (Closure).

    Повертає чисту функцію-валідатор, яка перевіряє min_val <= val <= max_val.
    """

    def validator(val: Any) -> None:
        if not isinstance(val, (int, float)):
            raise TypeError(
                f"Аргумент '{arg_name}' має бути числом (int/float), отримано: {type(val).__name__}"
            )
        if min_val is not None and val < min_val:
            raise ValueError(
                f"Аргумент '{arg_name}' повинен бути >= {min_val}, отримано: {val}"
            )
        if max_val is not None and val > max_val:
            raise ValueError(
                f"Аргумент '{arg_name}' повинен бути <= {max_val}, отримано: {val}"
            )

    return validator


def make_type_validator(
    expected_type: type,
    arg_name: str = "arg",
) -> Callable[[Any], None]:
    """Фабрика валідаторів типу аргументу (Closure).

    Повертає функцію-валідатор, що перевіряє isinstance(val, expected_type).
    """

    def validator(val: Any) -> None:
        if not isinstance(val, expected_type):
            raise TypeError(
                f"Аргумент '{arg_name}' повинен мати тип {expected_type.__name__}, отримано: {type(val).__name__}"
            )

    return validator


def make_predicate_validator(
    predicate: Callable[[Any], bool],
    error_message: str,
    arg_name: str = "arg",
) -> Callable[[Any], None]:
    """Фабрика валідаторів довільного предиката (Closure)."""

    def validator(val: Any) -> None:
        if not predicate(val):
            raise ValueError(
                f"Аргумент '{arg_name}' не пройшов валідацію: {error_message}"
            )

    return validator