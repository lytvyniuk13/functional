"""tests/test_core.py — Pytest-тести для перевірки чистоти функціонального ядра."""

from copy import deepcopy

import pytest

from core import (
    Order,
    Rental,
    base_price,
    calculate_base_price,
    compose,
    make_multiplier,
    make_processor,
    make_rental_processor,
    process_orders_pure,
    process_rentals_pure,
    stamp_record,
    stamp_total,
    with_rental_totals,
)

# --- Тести базових вимог методички (Завдання 1-3) ---


@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {
            "id": 1,
            "items": [{"price": 50.0, "qty": 2}, {"price": 20.0, "qty": 1}],
            "paid": True,
        },
        {"id": 2, "items": [{"price": 30.0, "qty": 1}], "paid": True},
        {"id": 3, "items": [{"price": 100.0, "qty": 2}], "paid": False},
        {"id": 4, "items": [{"price": 150.0, "qty": 1}], "paid": True},
    ]


def test_referential_transparency_orders(sample_orders: list[Order]) -> None:
    args = {"min_total": 100.0, "discount": 0.1, "tax_rate": 0.2}
    r1 = process_orders_pure(sample_orders, **args)
    r2 = process_orders_pure(sample_orders, **args)
    assert r1 == r2
    assert r1["count"] == 2
    assert r1["revenue"] == 291.6


def test_no_mutation_orders(sample_orders: list[Order]) -> None:
    original = deepcopy(sample_orders)
    process_orders_pure(sample_orders, min_total=0.0, discount=0.0, tax_rate=0.0)
    assert sample_orders == original
    for o in sample_orders:
        assert "total" not in o


def test_callable_policies_orders(sample_orders: list[Order]) -> None:
    accept = lambda s: s >= 50.0
    apply_discount = lambda s: s * 0.9
    apply_tax = lambda s: s * 1.2

    processor = make_processor(
        accept=accept, apply_discount=apply_discount, apply_tax=apply_tax
    )
    res = processor(sample_orders)
    assert res["count"] == 2
    assert res["revenue"] == 291.6


def test_stamp_total() -> None:
    tot, ts = stamp_total(150.0, lambda: 12345.0)
    assert tot == 150.0
    assert ts == 12345.0


# --- Тести Варіанта №9 (Прокат автомобілів) ---


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
    assert base_price(sample_rentals[1]) == 250.0


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
    assert "total" not in original
    assert updated is not original


def test_referential_transparency_rentals(sample_rentals: list[Rental]) -> None:
    r1 = process_rentals_pure(sample_rentals)
    r2 = process_rentals_pure(sample_rentals)
    assert r1 == r2
    assert r1["count"] == 3
    assert r1["revenue"] == 1530.90


def test_no_mutation_rentals(sample_rentals: list[Rental]) -> None:
    original = deepcopy(sample_rentals)
    process_rentals_pure(sample_rentals)
    assert sample_rentals == original


def test_callable_policies_rentals(sample_rentals: list[Rental]) -> None:
    custom_discount = lambda b, d: round(b * 0.20, 2)
    custom_insurance = lambda s, c: round(s * 0.10, 2)
    filter_all = lambda r: r.get("status") == "confirmed"

    processor = make_rental_processor(
        filter_policy=filter_all,
        discount_policy=custom_discount,
        insurance_policy=custom_insurance,
    )
    res = processor(sample_rentals)
    assert res["count"] == 3
    rentals: list[Rental] = res["rentals"]
    assert rentals[0]["total"] == 52.8


def test_compose_and_multiplier() -> None:
    fee1 = make_multiplier(1.10)
    fee2 = make_multiplier(1.05)
    total_calc = compose(fee2, fee1)
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
    stamped, ts = stamp_record(record, mock_now)
    assert ts == fixed_time
    assert stamped["id"] == record["id"]
    assert stamped is not record
