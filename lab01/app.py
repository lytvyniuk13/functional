"""
app.py — Оболонка побічних ефектів (Imperative Shell).
Відповідає за консольний ввід/вивід (I/O), конфігурацію політик через Callable,
демонстрацію інжекції часу та виведення звітів.
"""

import time
from datetime import datetime
from typing import Any

from core import (
    Rental,
    make_rental_processor,
    process_rentals_pure,
    stamp_record,
)


def render_report(
    result: dict[str, Any], title: str = "ЗВІТ СИСТЕМИ ПРОКАТУ АВТОМОБІЛІВ"
) -> None:
    """
    Імперативна функція вводу/виводу (I/O).
    Форматує та виводить результати обчислень у консоль у вигляді таблиці.
    Споживає виключно чистий словник-результат без внесення мутацій.
    """
    print("=" * 82)
    print(f"{title:^82}")
    print("=" * 82)
    print(
        f"{'ID':<4} | {'Клас авто':<10} | {'Днів':<5} | {'Ставка':<8} | "
        f"{'Базова':<9} | {'Знижка':<8} | {'Страховка':<10} | {'Разом':<9}"
    )
    print("-" * 82)

    rentals: list[Rental] = result.get("rentals", [])
    for r in rentals:
        print(
            f"{r['id']:<4} | "
            f"{r['car_class'].capitalize():<10} | "
            f"{r['days']:<5} | "
            f"${r['daily_rate']:<7.2f} | "
            f"${r.get('base_price', 0.0):<8.2f} | "
            f"-${r.get('discount_amount', 0.0):<7.2f} | "
            f"+${r.get('insurance_fee', 0.0):<9.2f} | "
            f"${r.get('total', 0.0):<8.2f}"
        )

    print("-" * 82)
    print(f"Кількість підтверджених замовлень: {result['count']}")
    print(f"Сумарна надана знижка:             -${result['total_discounts']:.2f}")
    print(f"Сумарний страховий збір:           +${result['total_insurance']:.2f}")
    print(f"Загальний виторг компанії:          ${result['revenue']:.2f}")
    print("=" * 82)


def main() -> None:
    # 1. Вхідний набір даних згідно зі специфікацією Варіанта №9
    raw_rentals: list[Rental] = [
        {
            "id": 101,
            "car_class": "economy",
            "days": 2,
            "daily_rate": 30.0,
            "status": "confirmed",  # 2 дні (<3) -> знижка 0%, страховка 5%
        },
        {
            "id": 102,
            "car_class": "standard",
            "days": 5,
            "daily_rate": 50.0,
            "status": "confirmed",  # 5 днів (3..6) -> знижка 10%, страховка 5%
        },
        {
            "id": 103,
            "car_class": "suv",
            "days": 4,
            "daily_rate": 85.0,
            "status": "cancelled",  # скасовано -> відсіюється фільтром
        },
        {
            "id": 104,
            "car_class": "suv",
            "days": 10,
            "daily_rate": 90.0,
            "status": "confirmed",  # 10 днів (>=7) -> знижка 15%, страховка 10%
        },
        {
            "id": 105,
            "car_class": "premium",
            "days": 7,
            "daily_rate": 180.0,
            "status": "confirmed",  # 7 днів (>=7) -> знижка 15%, страховка 15%
        },
        {
            "id": 106,
            "car_class": "economy",
            "days": 0,
            "daily_rate": 25.0,
            "status": "confirmed",  # 0 днів -> відсіюється фільтром
        },
        {
            "id": 107,
            "car_class": "premium",
            "days": 3,
            "daily_rate": 200.0,
            "status": "pending",  # pending -> відсіюється стандартним фільтром
        },
    ]

    # --- Демонстрація 1: Обробка за дефолтними політиками ядра ---
    default_report = process_rentals_pure(raw_rentals)
    render_report(default_report, title="СТАНДАРТНИЙ РОЗРАХУНОК (DEFAULT POLICIES)")

    # --- Демонстрація 2: Конфігурація кастомних політик через Callable ---
    # Приклад: промо-акція (Promo Weekend / VIP):
    # - Підвищена знижка за тривалість (25% від 7 днів, 15% від 3 днів)
    def promo_discount_policy(base_price: float, days: int) -> float:
        if days >= 7:
            return round(base_price * 0.25, 2)
        if days >= 3:
            return round(base_price * 0.15, 2)
        return 0.0

    # - Фіксована знижена страховка (7%) для всіх типів авто
    def flat_insurance_policy(subtotal: float, car_class: str) -> float:
        return round(subtotal * 0.07, 2)

    # - Розширений критерій валідності: допускаємо і 'confirmed', і 'pending'
    flexible_filter = (
        lambda r: r.get("status") in {"confirmed", "pending"} and r.get("days", 0) > 0
    )

    promo_processor = make_rental_processor(
        filter_policy=flexible_filter,
        discount_policy=promo_discount_policy,
        insurance_policy=flat_insurance_policy,
    )
    promo_report = promo_processor(raw_rentals)
    print()
    render_report(promo_report, title="АКЦІЙНИЙ РОЗРАХУНОК (CUSTOM CALLABLE POLICIES)")

    # --- Демонстрація 3: Інжекція недетермінованого часу (stamp_record) ---
    if default_report["rentals"]:
        first_record: Rental = default_report["rentals"][0]
        stamped_record, timestamp = stamp_record(first_record, time.time)
        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

        print()
        print(f"[Audit Log] Аудит замовлення ID #{stamped_record['id']}:")
        print(f"            Час фіксації:    {formatted_time} (UNIX: {timestamp:.4f})")
        print(f"            Підсумкова сума: ${stamped_record['total']:.2f}")


if __name__ == "__main__":
    main()
