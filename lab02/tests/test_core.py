"""tests/test_core.py — Pytest-тести для конвеєра лабораторної роботи №2 (Варіант №9)."""

from copy import deepcopy
from typing import List
import pytest

from core import (
    EmployeeRecord,
    build_pipeline,
    compose,
    juxt,
    pipe,
    reduce_stats,
)


@pytest.fixture
def sample_employees() -> List[EmployeeRecord]:
    return [
        {
            "id": 1,
            "name": "  ivan petrenko ",
            "department": "IT",
            "monthly_hours": [80.0, 85.0],  # 165.0 -> *1.15 = 189.75
        },
        {
            "id": 2,
            "name": "anna kovalchuk",
            "department": "HR",
            "monthly_hours": [40.0, 30.0],  # 70.0 (< 80) -> filtered out
        },
        {
            "id": 3,
            "name": "olena melnyk",
            "department": "Engineering",
            "monthly_hours": [90.0, 95.0],  # 185.0
        },
        {
            "id": 4,
            "name": "taras shevchenko",
            "department": "IT",
            "monthly_hours": [75.0, 85.0],  # 160.0 -> *1.15 = 184.0
        },
        {
            "id": 5,
            "name": "oksana boyko",
            "department": "Engineering",
            "monthly_hours": [90.0, 95.0],  # 185.0 (однакові години з ID 3)
        },
    ]


def test_referential_transparency(
    sample_employees: List[EmployeeRecord],
) -> None:
    pipeline = build_pipeline(
        top_n=3, department="IT", factor=1.15, min_hours=80.0
    )
    res1 = pipeline(sample_employees)
    res2 = pipeline(sample_employees)

    # Функціональна чистота: один і той самий вхід продукує ідентичний результат
    assert res1 == res2


def test_immutability(sample_employees: List[EmployeeRecord]) -> None:
    original = deepcopy(sample_employees)
    pipeline = build_pipeline(
        top_n=2, department="IT", factor=1.15, min_hours=50.0
    )
    _ = pipeline(sample_employees)

    # Вхідні словники та список не зазнали змін
    assert sample_employees == original
    for emp in sample_employees:
        assert "total_hours" not in emp


def test_top_n_and_sorting(sample_employees: List[EmployeeRecord]) -> None:
    pipeline = build_pipeline(
        top_n=3, department="IT", factor=1.15, min_hours=80.0
    )
    res = pipeline(sample_employees)

    assert len(res) == 3
    # ID 1 (189.75), ID 3 (185.0, менший id ніж 5), ID 5 (185.0)
    assert [r["id"] for r in res] == [1, 3, 5]
    assert res[0]["total_hours"] == 189.75
    assert res[1]["total_hours"] == 185.0
    assert res[2]["total_hours"] == 185.0
    assert res[0]["name"] == "Ivan Petrenko"


def test_tie_breaker_id_ascending() -> None:
    # Перевірка сортування за 2 ключами: при однакових годинах перевага у меншого id
    data: List[EmployeeRecord] = [
        {"id": 10, "name": "B", "department": "IT", "monthly_hours": [100.0]},
        {"id": 2, "name": "A", "department": "IT", "monthly_hours": [100.0]},
    ]
    pipeline = build_pipeline(
        top_n=2, department="IT", factor=1.0, min_hours=0.0
    )
    res = pipeline(data)

    assert [r["id"] for r in res] == [2, 10]


def test_reduce_stats(sample_employees: List[EmployeeRecord]) -> None:
    pipeline = build_pipeline(
        top_n=3, department="IT", factor=1.15, min_hours=80.0
    )
    res = pipeline(sample_employees)
    stats = reduce_stats(res)

    assert stats["count"] == 3.0
    assert stats["total_hours"] == 559.75
    assert stats["avg_hours"] == 186.58


def test_pipe_and_juxt_utilities() -> None:
    numbers = [1, 2, 3, 4]
    doubled_filtered = pipe(
        numbers,
        lambda seq: [x * 2 for x in seq],
        lambda seq: [x for x in seq if x > 4],
    )
    assert doubled_filtered == [6, 8]

    metrics = juxt(min, max, sum)([10, 20, 30])
    assert metrics == [10, 30, 60]