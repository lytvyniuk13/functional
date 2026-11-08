"""core.py — Pure-оновлення та бізнес-логіка розрахунків для системи доставки."""

from collections.abc import Mapping as MappingABC
from types import MappingProxyType
from typing import Any

from model import Parcel, RoutePoint


def add_route_point(
    parcel: Parcel, city: str, checkpoint: str, distance_km: float
) -> Parcel:
    """Чиста функція додавання нової точки маршруту."""
    point = RoutePoint(city=city, checkpoint=checkpoint, distance_km=distance_km)
    return parcel.with_route_point(point)


def add_label(parcel: Parcel, label: str) -> Parcel:
    """Чиста функція додавання логістичної мітки (наприклад, 'fragile', 'express')."""
    return parcel.with_label(label)


def change_status(parcel: Parcel, new_status: str) -> Parcel:
    """Чиста функція зміни статусу посилки."""
    return parcel.with_status(new_status)


def calculate_delivery_cost(
    parcel: Parcel,
    *,
    base_rate_per_km: float = 0.8,
    weight_factor: float = 1.2,
) -> float:
    """Чиста функція розрахунку вартості доставки з урахуванням міток і дистанції."""
    dist = parcel.total_distance()
    cost = dist * base_rate_per_km + (parcel.weight_kg * weight_factor * 10)

    if "express" in parcel.labels:
        cost *= 1.3
    if "fragile" in parcel.labels:
        cost += 50.0

    return round(cost, 2)


def freeze(obj: Any) -> Any:
    """Рекурсивне глибоке заморожування вкладених структур (Deep Freeze шаблон)."""
    if isinstance(obj, MappingABC):
        frozen_inner = {k: freeze(v) for k, v in obj.items()}
        return MappingProxyType(frozen_inner)
    if isinstance(obj, set):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)
    return obj
