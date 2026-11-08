"""tests/test_decorators.py — Pytest-тести для перевірки замикань та декораторів (Варіант №9)."""

from typing import List
import pytest

from closures import (
    make_counter,
    make_predicate_validator,
    make_range_validator,
    make_type_validator,
)
from decorators import logged, timed, validate


# --- 1. Тести замикань (Closures) ---


def test_make_counter_stateful_isolation() -> None:
    counter1 = make_counter(start=5)
    assert counter1() == 6
    assert counter1() == 7

    counter2 = make_counter(start=0)
    assert counter2() == 1
    # Стан counter1 лишається ізольованим від counter2
    assert counter1() == 8


def test_make_range_validator_success() -> None:
    validator = make_range_validator(
        min_val=10, max_val=50, arg_name="test_val"
    )
    validator(10)
    validator(25.5)
    validator(50)


def test_make_range_validator_out_of_bounds() -> None:
    validator = make_range_validator(min_val=10, max_val=50, arg_name="score")

    with pytest.raises(ValueError, match="повинен бути >= 10"):
        validator(9)

    with pytest.raises(ValueError, match="повинен бути <= 50"):
        validator(51)


def test_make_range_validator_wrong_type() -> None:
    validator = make_range_validator(min_val=0, max_val=100, arg_name="score")

    with pytest.raises(TypeError, match="має бути числом"):
        validator("invalid_string")


def test_make_type_validator() -> None:
    validator = make_type_validator(expected_type=str, arg_name="user_name")
    validator("Admin")

    with pytest.raises(TypeError, match="повинен мати тип str"):
        validator(12345)


def test_make_predicate_validator() -> None:
    is_even = make_predicate_validator(
        predicate=lambda n: n % 2 == 0,
        error_message="число має бути парним",
        arg_name="n",
    )
    is_even(4)

    with pytest.raises(ValueError, match="число має бути парним"):
        is_even(5)


# --- 2. Тести декоратора @validate ---


def test_validate_decorator_preserves_metadata() -> None:
    @validate(x=make_range_validator(min_val=0, max_val=10))
    def sample_func(x: int) -> int:
        """Sample function documentation."""
        return x * 2

    assert sample_func.__name__ == "sample_func"
    assert sample_func.__doc__ == "Sample function documentation."
    assert hasattr(sample_func, "__wrapped__")
    assert sample_func(4) == 8


def test_validate_decorator_positional_and_kwargs() -> None:
    @validate(
        count=make_range_validator(min_val=1, max_val=100, arg_name="count"),
        title=make_type_validator(expected_type=str, arg_name="title"),
    )
    def create_report(title: str, count: int) -> str:
        return f"{title}: {count}"

    # Перевірка з позиційними аргументами
    assert create_report("Summary", 10) == "Summary: 10"
    # Перевірка з іменованими аргументами
    assert create_report(count=5, title="Report") == "Report: 5"

    # Невалідний count (виходить за межі діапазону)
    with pytest.raises(ValueError, match="повинен бути >= 1"):
        create_report("Fail", 0)

    # Невалідний тип title
    with pytest.raises(TypeError, match="повинен мати тип str"):
        create_report(123, 10)  # type: ignore


# --- 3. Тести декоратора @timed з ін'єкцією залежностей ---


def test_timed_decorator_deterministic_clock() -> None:
    ticks = [10.0, 10.025]
    logs: List[str] = []

    @timed("fast_op", unit="ms", logger=logs.append, clock=lambda: ticks.pop(0))
    def do_work(a: int, b: int) -> int:
        return a + b

    result = do_work(10, 20)
    assert result == 30
    assert len(logs) == 1
    assert "[timed] fast_op took 25.000 ms" in logs[0]


def test_timed_decorator_logs_on_exception() -> None:
    ticks = [5.0, 5.002]
    logs: List[str] = []

    @timed(
        "failing_op", unit="s", logger=logs.append, clock=lambda: ticks.pop(0)
    )
    def buggy() -> None:
        raise RuntimeError("Fatal database failure")

    with pytest.raises(RuntimeError, match="Fatal database failure"):
        buggy()

    assert len(logs) == 1
    assert "[timed] failing_op took 0.002 s" in logs[0]


# --- 4. Тести декоратора @logged ---


def test_logged_decorator() -> None:
    logs: List[str] = []

    @logged("TEST_SVC", logger=logs.append)
    def divide(a: float, b: float) -> float:
        return a / b

    res = divide(10.0, 2.0)
    assert res == 5.0
    assert len(logs) == 2
    assert "Calling divide with args=(10.0, 2.0)" in logs[0]
    assert "divide returned 5.0" in logs[1]


# --- 5. Тести композиції декораторів ---


def test_composition_logged_timed_validate() -> None:
    logs: List[str] = []
    # 2 виклики clock для успіху (t0, finally) та 2 для виклику з помилкою
    ticks = [100.0, 100.05, 200.0, 200.01]

    @logged("SVC", logger=logs.append)
    @timed(
        "deposit", unit="ms", logger=logs.append, clock=lambda: ticks.pop(0)
    )
    @validate(
        amount=make_range_validator(
            min_val=1.0, max_val=10000.0, arg_name="amount"
        )
    )
    def deposit(account: str, amount: float) -> str:
        return f"Deposited ${amount:.2f} to {account}"

    # Успішне проходження ланцюжка
    res = deposit("UA12345", 250.0)
    assert res == "Deposited $250.00 to UA12345"
    assert any("Calling deposit" in log for log in logs)
    assert any("[timed] deposit took 50.000 ms" in log for log in logs)
    assert any("deposit returned" in log for log in logs)

    # Помилка валідації: @validate перериває виконання цільової функції
    with pytest.raises(ValueError, match="повинен бути >= 1.0"):
        deposit("UA12345", -50.0)

    assert any("deposit raised ValueError" in log for log in logs)