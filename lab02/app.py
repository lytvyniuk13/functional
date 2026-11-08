"""app.py — CLI точка входу (Imperative Shell).

Відповідає за зчитування аргументів командного рядка, завантаження JSON
файлу та виведення звіту в консоль.
"""

import argparse
import json
import os

from core import EmployeeRecord, build_pipeline, juxt, reduce_stats


def load_data(file_path: str) -> list[EmployeeRecord]:
    """Зчитує вхідні дані з JSON файлу або повертає тестовий набір за замовчуванням."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data: list[EmployeeRecord] = json.load(f)
            return data

    return [
        {
            "id": 1,
            "name": "ivan petrenko",
            "department": "IT",
            "monthly_hours": [80.0, 85.0],
        },
        {
            "id": 2,
            "name": "anna kovalchuk",
            "department": "HR",
            "monthly_hours": [40.0, 30.0],
        },
        {
            "id": 3,
            "name": "olena melnyk",
            "department": "Engineering",
            "monthly_hours": [90.0, 95.0],
        },
        {
            "id": 4,
            "name": "taras shevchenko",
            "department": "IT",
            "monthly_hours": [75.0, 85.0],
        },
        {
            "id": 5,
            "name": "oksana boyko",
            "department": "Engineering",
            "monthly_hours": [90.0, 95.0],
        },
    ]


def render_report(top_employees: list[EmployeeRecord], stats: dict[str, float]) -> None:
    """Виводить відформатовану таблицю рейтингу та підсумкову статистику в консоль."""
    print("=" * 66)
    print("      РЕЙТИНГ ПРАЦІВНИКІВ КОМПАНІЇ (ВАРІАНТ №9: TOP-N)      ")
    print("=" * 66)
    print(f"{'Ранг':<5} | {'ID':<4} | {'Ім’я':<18} | {'Відділ':<14} | {'Години':<8}")
    print("-" * 66)

    for rank, emp in enumerate(top_employees, start=1):
        print(
            f"{rank:<5} | "
            f"{emp['id']:<4} | "
            f"{emp['name']:<18} | "
            f"{emp['department']:<14} | "
            f"{emp.get('total_hours', 0.0):<8.2f}"
        )

    print("-" * 66)
    # Застосування комбінатора juxt для вилучення значень
    get_metrics = juxt(
        lambda s: int(s["count"]),
        lambda s: s["total_hours"],
        lambda s: s["avg_hours"],
    )
    count, total_h, avg_h = get_metrics(stats)

    print("РЕЗУЛЬТАТИ REDUCE-АГРЕГАЦІЇ:")
    print(f"• Кількість у Top-N (count):      {count}")
    print(f"• Сумарні години (total_hours):   {total_h:.2f} год.")
    print(f"• Середні години (avg_hours):     {avg_h:.2f} год.")
    print("=" * 66)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Конвеєр обробки годин працівників компанії (Функціональне програмування)"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="sample_data.json",
        help="Шлях до файлу JSON",
    )
    parser.add_argument(
        "--top", type=int, default=3, help="Кількість працівників у Top-N"
    )
    parser.add_argument(
        "--boost-dept",
        type=str,
        default="IT",
        help="Відділ для застосування коефіцієнта",
    )
    parser.add_argument(
        "--factor",
        type=float,
        default=1.15,
        help="Коефіцієнт підсилення годин",
    )
    parser.add_argument(
        "--min-hours",
        type=float,
        default=80.0,
        help="Мінімальний поріг відпрацьованих годин",
    )

    args = parser.parse_args()

    records = load_data(args.data)
    pipeline = build_pipeline(
        top_n=args.top,
        department=args.boost_dept,
        factor=args.factor,
        min_hours=args.min_hours,
    )

    processed_top = pipeline(records)
    stats = reduce_stats(processed_top)

    render_report(processed_top, stats)


if __name__ == "__main__":
    main()
