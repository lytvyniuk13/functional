"""tests/test_streams.py — Набір pytest-тестів для перевірки лінивих обчислень."""

from itertools import accumulate, count, islice
from typing import Iterator
import pytest
from streams import (
    ScheduleEntry,
    cyclic_schedule,
    drop,
    fib_stream,
    moving_average,
    sliding_window,
    take,
)


def test_cyclic_schedule_basic() -> None:
    shifts = ["Morning", "Evening", "Night", "Off"]
    sched = cyclic_schedule(shifts, start_day=1)
    plan = take(6, sched)

    expected = [
        ScheduleEntry(1, "Morning"),
        ScheduleEntry(2, "Evening"),
        ScheduleEntry(3, "Night"),
        ScheduleEntry(4, "Off"),
        ScheduleEntry(5, "Morning"),
        ScheduleEntry(6, "Evening"),
    ]
    assert plan == expected


def test_cyclic_schedule_empty() -> None:
    sched = cyclic_schedule([])
    assert list(sched) == []


def test_cyclic_schedule_custom_start_day() -> None:
    sched = cyclic_schedule(["Duty", "Rest"], start_day=100)
    plan = take(3, sched)
    assert plan == [
        ScheduleEntry(100, "Duty"),
        ScheduleEntry(101, "Rest"),
        ScheduleEntry(102, "Duty"),
    ]


def test_take_and_drop_on_infinite_stream() -> None:
    counter = count(1)
    assert take(4, counter) == [1, 2, 3, 4]
    # Наступний елемент лічильника — 5
    assert take(2, counter) == [5, 6]

    # Пропускаємо 3 елементи (7, 8, 9) і беремо 2 наступні
    dropped = drop(3, counter)
    assert take(2, dropped) == [10, 11]


def test_take_edge_cases() -> None:
    assert take(0, count(1)) == []

    with pytest.raises(ValueError):
        take(-1, count(1))


def test_drop_edge_cases() -> None:
    with pytest.raises(ValueError):
        list(drop(-5, [1, 2, 3]))


def test_sliding_window_basic() -> None:
    data = [1, 2, 3, 4, 5]
    windows = list(sliding_window(data, 3))
    assert windows == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]


def test_sliding_window_k_greater_than_len() -> None:
    # Якщо розмір вікна більший за довжину джерела — вікон немає
    data = [1, 2]
    assert list(sliding_window(data, 5)) == []


def test_sliding_window_invalid_k() -> None:
    with pytest.raises(ValueError):
        list(sliding_window([1, 2], 0))


def test_moving_average() -> None:
    values = [10.0, 20.0, 30.0, 40.0]
    # Вікна: (10, 20, 30) -> avg 20.0; (20, 30, 40) -> avg 30.0
    averages = list(moving_average(values, 3))
    assert averages == [20.0, 30.0]


def test_laziness_evaluation() -> None:
    """Підтвердження лінивості: генератор обчислює рівно стільки елементів, скільки запитано."""
    eval_count = 0

    def spy_generator() -> Iterator[int]:
        nonlocal eval_count
        for i in count(1):
            eval_count += 1
            yield i

    stream = spy_generator()
    pipeline = islice(stream, 5)

    # До моменту матеріалізації жоден елемент не обчислюється
    assert eval_count == 0

    result = list(pipeline)
    assert result == [1, 2, 3, 4, 5]
    # Обчислено строго 5 елементів
    assert eval_count == 5


def test_accumulate_working_days() -> None:
    shifts = ["Day", "Night", "Off", "Day"]
    is_work = (1 if s != "Off" else 0 for s in shifts)
    cum_work = list(accumulate(is_work))
    assert cum_work == [1, 2, 2, 3]


def test_fib_stream() -> None:
    first_10 = take(10, fib_stream())
    assert first_10 == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]