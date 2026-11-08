"""main.py — Демонстраційний модуль для Варіанта №9 (Циклічний розклад)."""

from itertools import accumulate
from streams import cyclic_schedule, drop, fib_stream, sliding_window, take


def main() -> None:
    print("=" * 66)
    print("      ЛАБОРАТОРНА РОБОТА №5: ЛІНИВІ ОБЧИСЛЕННЯ ТА ITERTOOLS    ")
    print("               ВАРІАНТ №9: ЦИКЛІЧНИЙ РОЗКЛАД ЗМІН              ")
    print("=" * 66)

    # 1. Формування базового патерну чергувань
    shift_pattern = ["Денна", "Нічна", "Відсипний", "Вихідний"]
    print(f"Базовий цикл змін ({len(shift_pattern)} дні): {shift_pattern}\n")

    # Створення нескінченного графіка чергувань
    schedule = cyclic_schedule(shift_pattern, start_day=1)

    # Отримання плану на перші 14 днів через take / islice
    plan_14_days = take(14, schedule)

    print("[1] ПЛАН РОБОТИ НА ПЕРШІ 14 ДНІВ (take + cycle + count + zip):")
    for entry in plan_14_days:
        status = (
            "Вільний день"
            if entry.shift in {"Відсипний", "Вихідний"}
            else "Робоча зміна"
        )
        print(f"  • День {entry.day:>2}: {entry.shift:<11} | [{status}]")

    # 2. Розрахунок ковзних вікон по 3 дні
    print("\n[2] КОВЗНІ ВІКНА ЗМІН (sliding_window k=3):")
    stream_for_windows = (
        entry.shift for entry in cyclic_schedule(shift_pattern, start_day=1)
    )
    first_5_windows = take(5, sliding_window(stream_for_windows, k=3))
    for idx, win in enumerate(first_5_windows, start=1):
        print(f"  • Вікно #{idx}: {win}")

    # 3. Накопичувальна кількість робочих днів через itertools.accumulate
    print("\n[3] ПРЕФІКСНА СТАТИСТИКА РОБОЧИХ ДНІВ (accumulate):")
    work_indicator = (
        1 if entry.shift in {"Денна", "Нічна"} else 0 for entry in plan_14_days
    )
    cumulative_work = list(accumulate(work_indicator))
    print(f"  • Накопичені відпрацьовані дні: {cumulative_work}")
    print(
        f"  • Загалом відпрацьовано {cumulative_work[-1]} з {len(plan_14_days)} днів"
    )

    # 4. Демонстрація drop та fib_stream
    print("\n[4] СТРІМ ФІБОНАЧЧІ ТА ПРОПУСК (drop + take):")
    fibs = fib_stream()
    dropped_5 = drop(5, fibs)
    next_8 = take(8, dropped_5)
    print(f"  • Перші 8 чисел Фібоначчі після пропуску 5 елементів: {next_8}")
    print("=" * 66)


if __name__ == "__main__":
    main()