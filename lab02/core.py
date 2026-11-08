"""
core.py — Чисте функціональне ядро для Варіанта №9: Працівники компанії.
Побудова конвеєра обробки на базі map, filter, reduce та функціональної композиції.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import Any, TypedDict, TypeVar


# Структура запису згідно з варіантом №9
class EmployeeRecord(TypedDict, total=False):
    id: int
    name: str
    department: str
    monthly_hours: list[float]
    total_hours: float  # додається в результаті чистих трансформацій


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


# --- Функціональні комбінатори ---


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Математична композиція функцій: compose(f, g, h)(x) == f(g(h(x)))."""

    def _c(x: Any) -> Any:
        for f in reversed(funcs):
            x = f(x)
        return x

    return _c


def pipe(data: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Прямий конвеєр трансформацій зліва направо: pipe(x, f, g) == g(f(x))."""
    acc = data
    for f in funcs:
        acc = f(acc)
    return acc


def juxt(*funcs: Callable[[Any], Any]) -> Callable[[Any], list[Any]]:
    """Повертає функцію, яка застосовує кожну функцію до одного й того ж аргументу."""
    return lambda x: [f(x) for f in funcs]


# --- Чисті трансформації (Pure Transformations) ---


def calculate_total_hours() -> (
    Callable[[Iterable[EmployeeRecord]], Iterator[EmployeeRecord]]
):
    """Трансформація (map): обчислює сумарні години без мутації вихідних даних."""
    return lambda recs: (
        {**r, "total_hours": round(float(sum(r.get("monthly_hours", []) or [])), 2)}
        for r in recs
    )


def boost_department_hours(
    department: str, factor: float
) -> Callable[[Iterable[EmployeeRecord]], Iterator[EmployeeRecord]]:
    """Трансформація (map): підсилює години працівників обраного відділу на заданий коефіцієнт."""

    def _boost(recs: Iterable[EmployeeRecord]) -> Iterator[EmployeeRecord]:
        for r in recs:
            curr = float(r.get("total_hours", 0.0))
            if r.get("department", "").strip().lower() == department.strip().lower():
                yield {**r, "total_hours": round(curr * factor, 2)}
            else:
                yield {**r, "total_hours": curr}

    return _boost


def filter_min_hours(
    min_hours: float = 80.0,
) -> Callable[[Iterable[EmployeeRecord]], Iterator[EmployeeRecord]]:
    """Трансформація (filter): відсіює працівників із годинами нижче мінімального порогу."""
    return lambda recs: (
        r for r in recs if float(r.get("total_hours", 0.0)) >= min_hours
    )


def normalize_names() -> Callable[[Iterable[EmployeeRecord]], Iterator[EmployeeRecord]]:
    """Трансформація (map): форматує імена у Title Case без зайвих пробілів."""
    return lambda recs: (
        {**r, "name": str(r.get("name", "")).strip().title()} for r in recs
    )


def sort_by_hours_desc() -> Callable[[Iterable[EmployeeRecord]], list[EmployeeRecord]]:
    """Сортування за 2 ключами: години спадно (-total_hours), тай-брейкер id зростаюче."""
    return lambda recs: sorted(
        recs, key=lambda r: (-float(r.get("total_hours", 0.0)), r.get("id", 0))
    )


def take(n: int) -> Callable[[Iterable[EmployeeRecord]], list[EmployeeRecord]]:
    """Зріз перших N елементів через islice (Top-N)."""
    return lambda recs: list(islice(recs, n))


# --- reduce-агрегація ---


def reduce_stats(recs: Iterable[EmployeeRecord]) -> dict[str, float]:
    """
    Агрегація за допомогою functools.reduce:
    обчислює count, total_hours та avg_hours.
    """
    init = {"count": 0.0, "total_hours": 0.0}
    acc = reduce(
        lambda a, r: {
            "count": a["count"] + 1,
            "total_hours": round(
                a["total_hours"] + float(r.get("total_hours", 0.0)), 2
            ),
        },
        recs,
        init,
    )
    avg = round(acc["total_hours"] / acc["count"], 2) if acc["count"] > 0 else 0.0
    return {
        "count": acc["count"],
        "total_hours": acc["total_hours"],
        "avg_hours": avg,
    }


# --- Складання конвеєра через композицію ---


def build_pipeline(
    top_n: int = 3,
    department: str = "IT",
    factor: float = 1.15,
    min_hours: float = 80.0,
) -> Callable[[Iterable[EmployeeRecord]], list[EmployeeRecord]]:
    """
    Будує чистий композиційний конвеєр перетворень:
    normalize -> calculate -> boost -> filter -> sort (2 keys) -> take(Top-N).
    """
    return compose(
        take(top_n),
        sort_by_hours_desc(),
        filter_min_hours(min_hours),
        boost_department_hours(department, factor),
        calculate_total_hours(),
        normalize_names(),
    )
