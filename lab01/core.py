"""
core.py — Чисте функціональне ядро для Варіанта №9: Прокат автомобілів.
Містить детерміновані чисті функції без побічних ефектів, глобальних змінних та мутацій.
"""

from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, List, Tuple, TypeVar, TypedDict


class Rental(TypedDict, total=False):
    id: int
    car_class: str      # 'economy', 'standard', 'suv', 'premium'
    days: int
    daily_rate: float
    status: str         # 'confirmed', 'pending', 'cancelled'
    base_price: float
    discount_amount: float
    insurance_fee: float
    total: float


FilterPolicyFn = Callable[[Rental], bool]
DiscountPolicyFn = Callable[[float, int], float]       # (base_price, days) -> discount_amount
InsurancePolicyFn = Callable[[float, str], float]      # (discounted_subtotal, car_class) -> insurance_fee
NowFn = Callable[[], float]                            # Інжекція часу без побічних ефектів

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


def stamp_record(record: Rental, now: NowFn) -> Tuple[Rental, float]:
    """Приклад ізоляції залежності від часу через інжекцію Callable."""
    return deepcopy(record), now()


# --- Функція вищого порядку (Фабрика обробника) ---

def make_rental_processor(
    *,
    filter_policy: FilterPolicyFn = default_rental_filter,
    discount_policy: DiscountPolicyFn = default_duration_discount,
    insurance_policy: InsurancePolicyFn = default_insurance_fee,
) -> Callable[[Iterable[Rental]], Dict[str, Any]]:
    """
    Фабрика, що конструює чистий конвеєр обробки з інжектованими політиками.
    """
    def process(rentals: Iterable[Rental]) -> Dict[str, Any]:
        processed_rentals: List[Rental] = []
        total_revenue = 0.0
        total_discount = 0.0
        total_insurance = 0.0

        for r in rentals:
            if not filter_policy(r):
                continue

            base = calculate_base_price(r)
            discount = discount_policy(base, r["days"])
            subtotal = base - discount
            insurance = insurance_policy(subtotal, r["car_class"])
            final_total = round(subtotal + insurance, 2)

            updated = with_rental_totals(
                r,
                base_price=base,
                discount_amount=discount,
                insurance_fee=insurance,
                total=final_total,
            )
            processed_rentals.append(updated)

            total_revenue += final_total
            total_discount += discount
            total_insurance += insurance

        return {
            "count": len(processed_rentals),
            "revenue": round(total_revenue, 2),
            "total_discounts": round(total_discount, 2),
            "total_insurance": round(total_insurance, 2),
            "rentals": processed_rentals,
        }

    return process


def process_rentals_pure(
    rentals: Iterable[Rental],
    *,
    filter_policy: FilterPolicyFn = default_rental_filter,
    discount_policy: DiscountPolicyFn = default_duration_discount,
    insurance_policy: InsurancePolicyFn = default_insurance_fee,
) -> Dict[str, Any]:
    """Прямий чистий виклик процесора замовлень."""
    processor = make_rental_processor(
        filter_policy=filter_policy,
        discount_policy=discount_policy,
        insurance_policy=insurance_policy,
    )
    return processor(rentals)