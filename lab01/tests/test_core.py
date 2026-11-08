"""
tests/test_core.py — Pytest-тести для перевірки чистоти функціонального ядра (Варіант №9).
"""

from copy import deepcopy

import pytest

from core import (
    Rental,
    calculate_base_price,
    compose,
    make_multiplier,
    make_rental_processor,
    process_rentals_pure,
    stamp_record,
    with_rental_totals,
)


@pytest.fixture
def sample_rentals() -> list[Rental]:
    return [
        {
            "id": 1,
            "car_class": "economy",
            "days": 2,
            "daily_rate": 30.0,
            "status": "confirmed",
        },
        {
            "id": 2,
            "car_class": "standard",
            "days": 5,
            "daily_rate": 50.0,
            "status": "confirmed",
        },
        {
            "id": 3,
            "car_class": "suv",
            "days": 4,
            "daily_rate": 85.0,
            "status": "cancelled",
        },
        {
            "id": 4,
            "car_class": "premium",
            "days": 7,
            "daily_rate": 180.0,
            "status": "confirmed",
        },
    ]


def test_calculate_base_price(sample_rentals: list[Rental]) -> None:
    assert calculate_base_price(sample_rentals[0]) == 60.0
    assert calculate_base_price(sample_rentals[1]) == 250.0


def test_with_rental_totals_immutability(sample_rentals: list[Rental]) -> None:
    original = sample_rentals[0]
    updated = with_rental_totals(
        original,
        base_price=60.0,
        discount_amount=0.0,
        insurance_fee=3.0,
        total=63.0,
    )

    assert updated["total"] == 63.0
    assert updated["base_price"] == 60.0
    assert "total" not in original
    assert "base_price" not in original
    assert updated is not original


def test_referential_transparency(sample_rentals: list[Rental]) -> None:
    # Той самий вхід гарантує ідентичний вихід без побічних ефектів
    r1 = process_rentals_pure(sample_rentals)
    r2 = process_rentals_pure(sample_rentals)

    assert r1 == r2
    assert r1["count"] == 3
    # ID 1: base 60.0, disc 0.0, ins 3.0 -> total 63.0
    # ID 2: base 250.0, disc 25.0, ins 11.25 -> total 236.25
    # ID 4: base 1260.0, disc 189.0, ins 160.65 -> total 1231.65
    # Загальний revenue: 63.0 + 236.25 + 1231.65 = 1530.90
    assert r1["revenue"] == 1530.90


def test_no_mutation(sample_rentals: list[Rental]) -> None:
    original = deepcopy(sample_rentals)
    process_rentals_pure(sample_rentals)

    # Вхідні дані абсолютно не мутуються
    assert sample_rentals == original
    for r in sample_rentals:
        assert "total" not in r


def test_callable_policies(sample_rentals: list[Rental]) -> None:
    # Перевірка гнучкої заміни політик через Callable
    custom_discount = lambda base, days: round(base * 0.20, 2)
    custom_insurance = lambda subtotal, car_class: round(subtotal * 0.10, 2)
    filter_all = lambda r: r.get("status") == "confirmed"

    processor = make_rental_processor(
        filter_policy=filter_all,
        discount_policy=custom_discount,
        insurance_policy=custom_insurance,
    )
    res = processor(sample_rentals)

    assert res["count"] == 3
    # ID 1: base 60, disc 12, sub 48, ins 4.8 -> total 52.8
    assert res["rentals"][0]["total"] == 52.8


def test_compose_and_multiplier() -> None:
    fee1 = make_multiplier(1.10)
    fee2 = make_multiplier(1.05)
    total_calc = compose(fee2, fee1)

    # 100 * 1.10 = 110.0 -> 110.0 * 1.05 = 115.5
    assert round(total_calc(100.0), 2) == 115.5


def test_stamp_record() -> None:
    fixed_time = 1700000000.0
    mock_now = lambda: fixed_time

    record: Rental = {
        "id": 1,
        "car_class": "economy",
        "days": 2,
        "daily_rate": 30.0,
    }
    _stamped, _ts = stamp_record(record, mock_now)
