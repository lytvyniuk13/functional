"""app.py — Демонстраційний модуль (Imperative Shell).

Ілюструє використання замикань, валідаторів та композиції декораторів.
"""

from closures import (
    make_counter,
    make_predicate_validator,
    make_range_validator,
)
from decorators import logged, timed, validate


# Бізнес-функція розрахунку оренди з повною композицією трьох декораторів
@logged("RENTAL_SERVICE")
@timed("calc_rental_cost", unit="ms")
@validate(
    days=make_range_validator(min_val=1, max_val=365, arg_name="days"),
    daily_rate=make_range_validator(
        min_val=10.0, max_val=5000.0, arg_name="daily_rate"
    ),
    car_class=make_predicate_validator(
        predicate=lambda s: s.lower()
        in {"economy", "standard", "suv", "premium"},
        error_message="дозволені класи: 'economy', 'standard', 'suv', 'premium'",
        arg_name="car_class",
    ),
)
def calculate_rental(
    days: int, daily_rate: float, car_class: str = "standard"
) -> float:
    """Розраховує вартість оренди автомобіля за заданими параметрами."""
    multiplier = {
        "economy": 1.0,
        "standard": 1.1,
        "suv": 1.25,
        "premium": 1.5,
    }[car_class.lower()]
    return round(days * daily_rate * multiplier, 2)


def main() -> None:
    print("=" * 66)
    print("   ЛАБОРАТОРНА РОБОТА №6: ЗАМИКАННЯ ТА ДЕКОРАТОРИ ЯК HOF    ")
    print("             ВАРІАНТ №9: ВАЛІДАЦІЯ АРГУМЕНТІВ               ")
    print("=" * 66)

    # 1. Демонстрація stateful closure
    print("\n[1] ДЕМОНСТРАЦІЯ STATEFUL CLOSURE (make_counter via nonlocal):")
    counter_a = make_counter(start=100)
    counter_b = make_counter(start=0)
    print(f"• Counter A (start 100): {counter_a()}, {counter_a()}, {counter_a()}")
    print(f"• Counter B (start 0):   {counter_b()}, {counter_b()}")
    print(f"• Counter A ізольований: {counter_a()} (стан незалежний)")

    # 2. Успішний виклик декорованої функції
    print(
        "\n[2] УСПІШНЕ ВИКОНАННЯ ДЕКОРОВАНОЇ ФУНКЦІЇ (@logged + @timed + @validate):"
    )
    total = calculate_rental(days=5, daily_rate=45.0, car_class="suv")
    print(f"✔ Розраховано суму: ${total:.2f}")

    # 3. Перевірка збереження метаданих (@functools.wraps)
    print("\n[3] ПЕРЕВІРКА ЗБЕРЕЖЕННЯ МЕТАДАНИХ:")
    print(f"• __name__: {calculate_rental.__name__}")
    print(f"• __doc__:  {calculate_rental.__doc__}")
    print(f"• __wrapped__ існує: {hasattr(calculate_rental, '__wrapped__')}")

    # 4. Демонстрація відловлювання помилок валідації
    print("\n[4] ДЕМОНСТРАЦІЯ ВАЛІДАЦІЇ НЕКОРЕКТНИХ АРГУМЕНТІВ:")

    # Помилка: від'ємні дні
    try:
        calculate_rental(days=-2, daily_rate=50.0)
    except ValueError as err:
        print(f"  ✖ Спіймано ValueError: {err}")

    # Помилка: невалідний клас автомобіля
    try:
        calculate_rental(days=3, daily_rate=40.0, car_class="spaceship")
    except ValueError as err:
        print(f"  ✖ Спіймано ValueError: {err}")

    # Помилка: невірний тип ставки
    try:
        calculate_rental(days=3, daily_rate="forty")  # type: ignore
    except TypeError as err:
        print(f"  ✖ Спіймано TypeError: {err}")

    print("=" * 66)


if __name__ == "__main__":
    main()