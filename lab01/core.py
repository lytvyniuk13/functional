"""
core.py — Чисте функціональне ядро для Варіанта №9: Прокат автомобілів.
Містить детерміновані чисті функції без побічних ефектів, глобальних змінних та мутацій.
"""

from collections.abc import Callable, Iterable
from copy import deepcopy
from typing import Any, TypedDict, TypeVar


class Rental(TypedDict, total=False):
    id: int
    car_class: str  # 'economy', 'standard', 'suv', 'premium'
    days: int
    daily_rate: float
    status: str  # 'confirmed', 'pending', 'cancelled'
    base_price: float
    discount_amount: float
    insurance_fee: float
    total: float


FilterPolicyFn = Callable[[Rental], bool]
DiscountPolicyFn = Callable[
    [float, int], float
]  # (base_price, days) -> discount_amount
InsurancePolicyFn = Callable[
    [float, str], float
]  # (discounted_subtotal, car_class) -> insurance_fee
NowFn = Callable[[], float]  # Інжекція часу без побічних ефектів

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def compose(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    """Математична композиція двох функцій: f(g(x))."""
    return lambda x: f(g(x))


def make_multiplier(k: float) -> Callable[[float], float]:
    """Фабрика множників (замикання)."""
    return lambda x: round(x * k, 2)


# --- Чисті функції предметної області (Варіант №9) ---


def calculate_base_price(rental: Rental) -> float:
    """Обчислює базову вартість оренди: дні * денна ставка."""
    return round(rental["days"] * rental["daily_rate"], 2)


def default_duration_discount(base_price: float, days: int) -> float:
    """
    Політика знижки за тривалістю:
    - від 7 днів: 15%
    - від 3 до 6 днів: 10%
    - менше 3 днів: 0%
    """
    if days >= 7:
        return round(base_price * 0.15, 2)
    if days >= 3:
        return round(base_price * 0.10, 2)
    return 0.0


def default_insurance_fee(subtotal: float, car_class: str) -> float:
    """
    Політика розрахунку обов'язкового страхового збору за класом авто:
    - premium: 15%
    - suv: 10%
    - economy / standard: 5%
    """
    rates = {
        "premium": 0.15,
        "suv": 0.10,
        "standard": 0.05,
        "economy": 0.05,
    }
    rate = rates.get(car_class.lower(), 0.05)
    return round(subtotal * rate, 2)


def default_rental_filter(rental: Rental) -> bool:
    """Критерій валідності: статус 'confirmed' та тривалість більше 0 днів."""
    return rental.get("status") == "confirmed" and rental.get("days", 0) > 0


def with_rental_totals(
    rental: Rental,
    *,
    base_price: float,
    discount_amount: float,
    insurance_fee: float,
    total: float,
) -> Rental:
    """
    Повертає новий словник із розрахованими показниками,
    гарантуючи незмінність (immutability) вхідного об'єкта.
    """
    return {
        **rental,
        "base_price": base_price,
        "discount_amount": discount_amount,
        "insurance_fee": insurance_fee,
        "total": total,
    }

