"""
mutable_model.py — Мутабельна предметна модель для Варіанта №9 (Система доставки).
Використовується автотестами для порівняння з незмінною моделлю.
"""

from typing import Any


class RoutePoint:
    def __init__(self, city: str, checkpoint: str, distance_km: float) -> None:
        self.city = city
        self.checkpoint = checkpoint
        self.distance_km = distance_km

    def __repr__(self) -> str:
        return f"RoutePoint({self.city!r}, {self.checkpoint!r}, {self.distance_km})"


class Parcel:
    def __init__(
        self,
        id: int,
        weight_kg: float,
        status: str,
        route: list[RoutePoint] | None = None,
        labels: set[str] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        self.id = id
        self.weight_kg = weight_kg
        self.status = status
        self.route: list[RoutePoint] = route if route is not None else []
        self.labels: set[str] = labels if labels is not None else set()
        self.meta: dict[str, Any] = meta if meta is not None else {}

    def total_distance(self) -> float:
        return sum(pt.distance_km for pt in self.route)

    def add_route_point(self, pt: RoutePoint) -> None:
        self.route.append(pt)

    def add_label(self, label: str) -> None:
        self.labels.add(label)

    def change_status(self, new_status: str) -> None:
        self.status = new_status
