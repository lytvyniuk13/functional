"""app.py — Демонстраційний модуль (Imperative Shell).

Ілюструє життєвий цикл незмінної посилки, pure updates та захист від мутацій.
"""

from dataclasses import FrozenInstanceError

from core import (
    add_label,
    add_route_point,
    calculate_delivery_cost,
    change_status,
    freeze,
)
from model import Parcel, RoutePoint, make_meta


def render_parcel_info(title: str, p: Parcel) -> None:
    """I/O функція форматованого відображення стану посилки."""
    print("-" * 68)
    print(f"[{title}]")
    print(f"• ID: {p.id} | Статус: {p.status.upper()} | Вага: {p.weight_kg} кг")
    print(f"• Мітки (Labels): {', '.join(sorted(p.labels)) if p.labels else 'немає'}")
    print("• Маршрут доставки:")
    for idx, pt in enumerate(p.route, start=1):
        print(f"   {idx}. {pt.city} ({pt.checkpoint}) — {pt.distance_km} км")
    print(f"• Загальна дистанція: {p.total_distance()} км")
    print(f"• Орієнтовна вартість: ${calculate_delivery_cost(p):.2f}")
    print(f"• Метадані (meta): {dict(p.meta)}")


def main() -> None:
    print("=" * 68)
    print("      СИСТЕМА ДОСТАВКИ ПОСИЛОК: ІМУТАБЕЛЬНА МОДЕЛЬ (ВАРІАНТ №9)     ")
    print("=" * 68)

    # 1. Створення початкової незмінної посилки
    start_point = RoutePoint(city="Львів", checkpoint="Відділення №1", distance_km=10.0)
    initial_parcel = Parcel(
        id=9001,
        weight_kg=4.2,
        status="pending",
        route=(start_point,),
        labels=frozenset({"standard"}),
        meta=make_meta(
            sender="Ярослав",
            recipient="Галина",
            declared_value_uah=2500,
            service="NovaPost",
        ),
    )
    render_parcel_info("1. СТВОРЕННЯ ПОСИЛКИ", initial_parcel)

    # 2. Pure update: додавання точок маршруту
    p_route = add_route_point(initial_parcel, "Рівне", "Транзитний HUB-Захід", 210.0)
    p_route = add_route_point(p_route, "Київ", "Центральне відділення №14", 330.0)
    render_parcel_info("2. ПІСЛЯ ДОДАВАННЯ ТОЧОК МАРШРУТУ", p_route)

    # 3. Pure update: додавання міток
    p_labeled = add_label(p_route, "fragile")
    p_labeled = add_label(p_labeled, "express")
    render_parcel_info("3. ПІСЛЯ ДОДАВАННЯ МІТОК (FRAGILE, EXPRESS)", p_labeled)

    # 4. Pure update: зміна статусів
    p_transit = change_status(p_labeled, "in_transit")
    p_delivered = change_status(p_transit, "delivered")
    render_parcel_info("4. ФІНАЛЬНИЙ СТАН (DELIVERED)", p_delivered)

    # 5. Демонстрація збереження початкового об'єкта
    print("-" * 68)
    print("[ПЕРЕВІРКА НЕЗМІННОСТІ ПОЧАТКОВОГО ОБ'ЄКТА]")
    print(f"• Початковий ID 9001 статус: {initial_parcel.status}")
    print(
        f"• Точок у початковому маршруті: {len(initial_parcel.route)} (у фінальному: {len(p_delivered.route)})"
    )
    print(f"• Початковий об'єкт is фінальний: {initial_parcel is p_delivered}")

    # 6. Перевірка рантайм-захисту від мутацій
    print("-" * 68)
    print("[ТЕСТУВАННЯ ЗАХИСТУ ВІД МУТАЦІЙ У РАНТАЙМІ]")
    try:
        initial_parcel.status = "hacked"  # type: ignore
    except FrozenInstanceError as e:
        print(
            f"✔ Захист @dataclass(frozen=True): {type(e).__name__} — пряма мутація заборонена!"
        )

    try:
        initial_parcel.meta["recipient"] = "Hacker"  # type: ignore
    except TypeError as e:
        print(f"✔ Захист MappingProxyType: {type(e).__name__} — {e}")

    # 7. Глибоке заморожування конфігурації
    raw_config = {
        "tariff_zones": ["West", "Center", "East"],
        "discounts": {"business": 0.15},
        "flags": {"auto_notify", "insurance"},
    }
    frozen_cfg = freeze(raw_config)
    print("-" * 68)
    print(
        f"✔ freeze() успішно створив: {type(frozen_cfg).__name__} "
        f"з вкладеними {type(frozen_cfg['tariff_zones']).__name__} та {type(frozen_cfg['flags']).__name__}"
    )
    print("=" * 68)


if __name__ == "__main__":
    main()
