"""tests/test_performance.py — Порівняльний аналіз швидкодії in-place змін та pure updates."""

import time
from typing import Any, List, Set
import pytest

from core import add_label, add_route_point, change_status
from model import Parcel, RoutePoint, make_meta


# Мутабельний аналог (Baseline) для порівняння часу
class MutableRoutePoint:
    __slots__ = ("city", "checkpoint", "distance_km")

    def __init__(self, city: str, checkpoint: str, distance_km: float):
        self.city = city
        self.checkpoint = checkpoint
        self.distance_km = distance_km


class MutableParcel:
    __slots__ = ("id", "weight_kg", "status", "route", "labels", "meta")

    def __init__(
        self,
        id: int,
        weight_kg: float,
        status: str,
        route: List[MutableRoutePoint],
        labels: Set[str],
        meta: dict[str, Any],
    ):
        self.id = id
        self.weight_kg = weight_kg
        self.status = status
        self.route = route
        self.labels = labels
        self.meta = meta

    def add_route_point(self, pt: MutableRoutePoint) -> None:
        self.route.append(pt)

    def add_label(self, label: str) -> None:
        self.labels.add(label)

    def change_status(self, new_status: str) -> None:
        self.status = new_status


def test_benchmark_mutable_vs_immutable_updates() -> None:
    iterations = 5000

    # 1. Замір часу мутабельної моделі
    t0_mut = time.perf_counter()
    for i in range(iterations):
        p_mut = MutableParcel(
            id=i,
            weight_kg=2.5,
            status="pending",
            route=[MutableRoutePoint("Lviv", "WH-1", 10.0)],
            labels={"standard"},
            meta={"sender": "User"},
        )
        p_mut.add_route_point(MutableRoutePoint("Kyiv", "HUB-Main", 540.0))
        p_mut.add_label("express")
        p_mut.change_status("in_transit")
    duration_mut = time.perf_counter() - t0_mut

    # 2. Замір часу незмінної моделі (Pure Updates)
    t0_immut = time.perf_counter()
    for i in range(iterations):
        p_immut = Parcel(
            id=i,
            weight_kg=2.5,
            status="pending",
            route=(RoutePoint("Lviv", "WH-1", 10.0),),
            labels=frozenset({"standard"}),
            meta=make_meta(sender="User"),
        )
        p_immut = add_route_point(p_immut, "Kyiv", "HUB-Main", 540.0)
        p_immut = add_label(p_immut, "express")
        p_immut = change_status(p_immut, "in_transit")
    duration_immut = time.perf_counter() - t0_immut

    overhead_per_op_us = (duration_immut - duration_mut) / iterations * 1e6

    print(f"\n[Результати бенчмарку на {iterations} операцій]:")
    print(
        f"• Мутабельні in-place операції: {duration_mut:.4f} с ({duration_mut / iterations * 1e6:.2f} мкс/іт)"
    )
    print(
        f"• Незмінні pure updates:        {duration_immut:.4f} с ({duration_immut / iterations * 1e6:.2f} мкс/іт)"
    )
    print(
        f"• Накладні витрати на копіювання: {overhead_per_op_us:.2f} мкс на повний цикл життєвого циклу"
    )

    # Незмінні оновлення мають вкладатися у розумний ліміт (< 1.0 с на 5000 ітерацій)
    assert duration_immut < 1.0