"""streams.py — Ліниві генератори та операції над потоками даних (Варіант №9).

Містить нескінченний циклічний розклад, утиліти take/drop,
ковзні вікна (sliding_window) та числовий стрім Фібоначчі.
"""

from collections import deque
from itertools import count, cycle, islice
from typing import Iterable, Iterator, List, NamedTuple, Tuple, TypeVar

T = TypeVar("T")


class ScheduleEntry(NamedTuple):
    """Незмінний запис одного дня графіка змін: порядковий номер та назва зміни."""

    day: int
    shift: str


def cyclic_schedule(
    shifts: Iterable[str], start_day: int = 1
) -> Iterator[ScheduleEntry]:
    """Нескінченний генератор циклічного розкладу (Варіант №9).

    Використовує:
    - itertools.cycle для нескінченного зациклення переданого списку змін;
    - itertools.count для послідовної нумерації календарних днів;
    - zip для їх синхронного лінивого об'єднання.
    """
    shift_list = list(shifts)
    if not shift_list:
        return

    day_counter = count(start=start_day)
    shift_cycler = cycle(shift_list)

    for day, shift in zip(day_counter, shift_cycler):
        yield ScheduleEntry(day, shift)


def take(n: int, it: Iterable[T]) -> List[T]:
    """Ліниво відбирає перші n елементів і повертає їх у вигляді списку.

    Матеріалізує лише запитані n елементів, не чіпаючи решту потоку.
    """
    if n < 0:
        raise ValueError("Параметр n має бути невід'ємним числом")
    return list(islice(it, n))


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    """Пропускає перші n елементів потоку без матеріалізації проміжних даних."""
    if n < 0:
        raise ValueError("Параметр n має бути невід'ємним числом")
    it_obj = iter(it)
    next(islice(it_obj, n, n), None)
    return it_obj


def sliding_window(it: Iterable[T], k: int) -> Iterator[Tuple[T, ...]]:
    """Формує ліниве ковзне вікно розміру k над потоком елементів.

    Побудовано на базі collections.deque(maxlen=k) з ефективністю O(1) на крок
    та фіксованим використанням пам'яті O(k).
    """
    if k <= 0:
        raise ValueError("Розмір вікна k має бути більшим за 0")

    it_obj = iter(it)
    dq: deque[T] = deque(maxlen=k)

    # Заповнюємо перше вікно розміру k
    for _ in range(k):
        try:
            dq.append(next(it_obj))
        except StopIteration:
            return  # Якщо довжина джерела менша за k — жодне вікно не утворюється

    yield tuple(dq)

    # Зсув вікна: додавання виштовхує найстаріший елемент
    for item in it_obj:
        dq.append(item)
        yield tuple(dq)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    """Лінивий розрахунок простого ковзного середнього (SMA) для вікна k."""
    for window in sliding_window(it, k):
        yield round(sum(window) / k, 4)


def fib_stream() -> Iterator[int]:
    """Нескінченний генератор чисел послідовності Фібоначчі."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b