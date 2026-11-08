"""model.py — Незмінні структури даних для Варіанта №9: Система доставки.

Використовує NamedTuple, @dataclass(frozen=True, slots=True) та
MappingProxyType.
"""

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, Mapping, NamedTuple, Tuple


class RoutePoint(NamedTuple):
    """Незмінна точка маршруту доставки: місто, назва чекпоінту, відстань."""

    city: str
    checkpoint: str
    distance_km: float


def make_meta(**kwargs: Any) -> MappingProxyType:
    """Створює захищений тільки-для-читання словник метаданих.

    Попередньо копіює джерело dict(kwargs), щоб уникнути зовнішніх мутацій.
    """
    return MappingProxyType(dict(kwargs))


@dataclass(frozen=True, slots=True)
class Parcel:
    """Незмінна посилка в системі логістики.

    frozen=True генерує __hash__ і забороняє reassignment атрибутів;
    slots=True оптимізує пам'ять і пришвидшує доступ до полів.
    """

    id: int
    weight_kg: float
    status: str  # 'pending', 'in_transit', 'delivered', 'cancelled'
    route: Tuple[RoutePoint, ...]  # незмінний кортеж (НЕ list)
    labels: frozenset[str]  # незмінна множина міток (НЕ set)
    meta: Mapping[str, Any]  # read-only view MappingProxyType (НЕ dict)

    def total_distance(self) -> float:
        """Обчислює загальну дистанцію за всіма точками маршруту."""
        return round(sum(point.distance_km for point in self.route), 2)

    def with_route_point(self, point: RoutePoint) -> "Parcel":
        """Pure update: повертає новий Parcel із доданою точкою через конкатенацію tuple."""
        return replace(self, route=self.route + (point,))

    def with_label(self, label: str) -> "Parcel":
        """Pure update: повертає новий Parcel із новою міткою через об'єднання frozenset."""
        return replace(self, labels=self.labels | frozenset({label}))

    def with_status(self, new_status: str) -> "Parcel":
        """Pure update: повертає новий Parcel зі зміненим статусом через dataclasses.replace."""
        return replace(self, status=new_status)