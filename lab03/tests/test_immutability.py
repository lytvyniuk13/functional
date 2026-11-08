"""tests/test_immutability.py — Pytest-тести для перевірки незмінності моделі доставки."""

from dataclasses import FrozenInstanceError
from types import MappingProxyType
import pytest

from core import (
    add_label,
    add_route_point,
    calculate_delivery_cost,
    change_status,
    freeze,
)
from model import Parcel, RoutePoint, make_meta


@pytest.fixture
def sample_parcel() -> Parcel:
    pt = RoutePoint(city="Lviv", checkpoint="Warehouse-1", distance_km=15.0)
    return Parcel(
        id=101,
        weight_kg=3.0,
        status="pending",
        route=(pt,),
        labels=frozenset({"standard"}),
        meta=make_meta(
            sender="Yaroslav", recipient="Halyna", delivery_type="ground"
        ),
    )


def test_pure_update_adds_route_point(sample_parcel: Parcel) -> None:
    updated = add_route_point(
        sample_parcel, city="Kyiv", checkpoint="Hub-Center", distance_km=540.0
    )

    # Вихідний об'єкт не змінився
    assert len(sample_parcel.route) == 1
    assert sample_parcel.total_distance() == 15.0

    # Новий об'єкт містить обидві точки маршруту
    assert len(updated.route) == 2
    assert updated.total_distance() == 555.0
    assert updated is not sample_parcel


def test_pure_update_adds_label(sample_parcel: Parcel) -> None:
    updated = add_label(sample_parcel, "fragile")

    assert "fragile" not in sample_parcel.labels
    assert "fragile" in updated.labels
    assert "standard" in updated.labels
    assert updated is not sample_parcel


def test_pure_update_changes_status(sample_parcel: Parcel) -> None:
    updated = change_status(sample_parcel, "in_transit")

    assert sample_parcel.status == "pending"
    assert updated.status == "in_transit"
    assert updated is not sample_parcel


def test_no_mutation_guarantee(sample_parcel: Parcel) -> None:
    # Фіксуємо початковий зріз значень
    orig_id = sample_parcel.id
    orig_status = sample_parcel.status
    orig_route = sample_parcel.route
    orig_labels = sample_parcel.labels
    orig_meta = dict(sample_parcel.meta)

    # Серія pure-оновлень
    p1 = add_route_point(sample_parcel, "Rivne", "Hub-West", 210.0)
    p2 = add_label(p1, "express")
    _ = change_status(p2, "delivered")

    # Переконуємося, що первинний об'єкт лишився на 100% незмінним
    assert sample_parcel.id == orig_id
    assert sample_parcel.status == orig_status
    assert sample_parcel.route == orig_route
    assert sample_parcel.labels == orig_labels
    assert dict(sample_parcel.meta) == orig_meta


def test_frozen_dataclass_prevents_reassignment(sample_parcel: Parcel) -> None:
    with pytest.raises(FrozenInstanceError):
        sample_parcel.status = "tampered"  # type: ignore

    with pytest.raises(FrozenInstanceError):
        sample_parcel.weight_kg = 999.0  # type: ignore


def test_mappingproxy_is_read_only(sample_parcel: Parcel) -> None:
    with pytest.raises(TypeError):
        sample_parcel.meta["recipient"] = "Intruder"  # type: ignore

    with pytest.raises(TypeError):
        sample_parcel.meta["new_field"] = "Value"  # type: ignore


def test_hashability_route_point() -> None:
    # NamedTuple з незмінними примітивними полями є хешованим
    pt1 = RoutePoint(city="Lviv", checkpoint="Warehouse-1", distance_km=15.0)
    pt2 = RoutePoint(city="Lviv", checkpoint="Warehouse-1", distance_km=15.0)

    points_set = {pt1, pt2}
    assert len(points_set) == 1

    cache = {pt1: "HUB-1"}
    assert cache[pt2] == "HUB-1"


def test_parcel_hashability_explanation(sample_parcel: Parcel) -> None:
    # MappingProxyType у стандартному Python не реалізує __hash__,
    # тому @dataclass(frozen=True) з таким полем викидає TypeError при hash(parcel).
    with pytest.raises(TypeError) as exc_info:
        hash(sample_parcel)
    assert "unhashable type: 'mappingproxy'" in str(exc_info.value)


def test_calculate_delivery_cost(sample_parcel: Parcel) -> None:
    base_cost = calculate_delivery_cost(sample_parcel)
    # dist: 15.0 * 0.8 = 12.0; weight: 3.0 * 1.2 * 10 = 36.0 -> 48.0
    assert base_cost == 48.0

    express_fragile = add_label(add_label(sample_parcel, "express"), "fragile")
    cost = calculate_delivery_cost(express_fragile)
    # (12.0 + 36.0) * 1.3 + 50.0 = 48.0 * 1.3 + 50.0 = 112.4
    assert cost == 112.4


def test_deep_freeze_utility() -> None:
    raw = {
        "cities": ["Lviv", "Kyiv"],
        "hubs": {"hub1", "hub2"},
        "cfg": {"sub": [1, 2]},
    }
    frozen_res = freeze(raw)

    assert isinstance(frozen_res, MappingProxyType)
    assert isinstance(frozen_res["cities"], tuple)
    assert isinstance(frozen_res["hubs"], frozenset)
    assert isinstance(frozen_res["cfg"], MappingProxyType)
    assert isinstance(frozen_res["cfg"]["sub"], tuple)