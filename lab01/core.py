"""core.py — Чисте функціональне ядро (ЛР №1).

Містить базові чисті функції (Завдання 1–3) та функції Варіанта №9 (Прокат автомобілів).
"""

from collections.abc import Callable, Iterable
from copy import deepcopy
from typing import Any, TypedDict, TypeVar

# ============================================================================
# 1. БАЗОВА ЧАСТИНА (Завдання 1, 2, 3 методичних вказівок)
# ============================================================================


class Item(TypedDict):
    price: float
    qty: int


class Order(TypedDict, total=False):
    id: int
    items: list[Item]
    paid: bool
    total: float


SubtotalFn = Callable[[float], float]
DiscountFn = Callable[[float], float]
TaxFn = Callable[[float], float]
FilterFn = Callable[[float], bool]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Математична композиція двох функцій: f(g(x))."""
    return lambda x: f(g(x))


def make_multiplier(k: float) -> Callable[[Any], Any]:
    """Фабрика множників (Currying/Closure)."""
    return lambda x: x * k


def order_subtotal(order: Order) -> float:
    """Обчислює базову суму замовлення."""
    return sum(it["price"] * it["qty"] for it in order.get("items", []))


def with_total(order: Any, total: float) -> Any:
    """Повертає новий словник із розрахованим полем total без мутацій."""
    return {**order, "total": round(total, 2)}


def process_orders_pure(
    orders: Iterable[Order],
    *,
    min_total: float,
    discount: float,
    tax_rate: float,
) -> dict[str, Any]:
    """Базова чиста функція обробки замовлень (Завдання 1)."""
    qualified: list[Order] = []
    revenue = 0.0

    for o in orders:
        if not o.get("paid", False):
            continue
        subtotal = order_subtotal(o)
        if subtotal < min_total:
            continue
        total = subtotal * (1.0 - discount) * (1.0 + tax_rate)
        new_o = with_total(o, total)
        qualified.append(new_o)
        revenue += total

    return {
        "count": len(qualified),
        "revenue": round(revenue, 2),
        "orders": qualified,
        "rentals": qualified,
    }


def make_processor(
    *,
    accept: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: TaxFn,
) -> Callable[[Iterable[Order]], dict[str, Any]]:
    """Фабрика функцій вищого порядку (Завдання 2)."""

    def process(orders: Iterable[Order]) -> dict[str, Any]:
        qualified: list[Order] = []
        revenue = 0.0

        for o in orders:
            if not o.get("paid", False):
                continue
            subtotal = order_subtotal(o)
            if not accept(subtotal):
                continue
            total = apply_tax(apply_discount(subtotal))
            qualified.append(with_total(o, total))
            revenue += total

        return {
            "count": len(qualified),
            "revenue": round(revenue, 2),
            "orders": qualified,
            "rentals": qualified,
        }

    return process


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    """Ізоляція недетермінованого джерела часу (Завдання 3)."""
    return round(total, 2), now()


# ============================================================================
# 2. ВАРІАНТ №9: ПРОКАТ АВТОМОБІЛІВ
# ============================================================================


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
DiscountPolicyFn = Callable[[float, int], float]
InsurancePolicyFn = Callable[[float, str], float]


def calculate_base_price(rental: Rental) -> float:
    """Обчислює базову вартість оренди: дні * денна ставка."""
    return round(rental["days"] * rental["daily_rate"], 2)


base_price = calculate_base_price


def default_duration_discount(base_price_val: float, days: int) -> float:
    """Політика знижки за тривалістю."""
    if days >= 7:
        return round(base_price_val * 0.15, 2)
    if days >= 3:
        return round(base_price_val * 0.10, 2)
    return 0.0


def default_insurance_fee(subtotal: float, car_class: str) -> float:
    """Політика розрахунку обов'язкового страхового збору за класом авто."""
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
    """Повертає новий словник із розрахованими показниками без мутацій."""
    return {
        **rental,
        "base_price": base_price,
        "discount_amount": discount_amount,
        "insurance_fee": insurance_fee,
        "total": total,
    }


def stamp_record(record: Rental, now: NowFn) -> tuple[Rental, float]:
    """Ізоляція залежності від часу для оренди."""
    return deepcopy(record), now()


def make_rental_processor(
    *,
    filter_policy: FilterPolicyFn = default_rental_filter,
    discount_policy: DiscountPolicyFn = default_duration_discount,
    insurance_policy: InsurancePolicyFn = default_insurance_fee,
) -> Callable[[Iterable[Rental]], dict[str, Any]]:
    """Фабрика обробника оренди з інжектованими політиками."""

    def process(rentals: Iterable[Rental]) -> dict[str, Any]:
        processed_rentals: list[Rental] = []
        total_revenue = 0.0
        total_discount = 0.0
        total_insurance = 0.0

        for r in rentals:
            if not filter_policy(r):
                continue

            b_price = calculate_base_price(r)
            discount = discount_policy(b_price, r["days"])
            subtotal = b_price - discount
            insurance = insurance_policy(subtotal, r["car_class"])
            final_total = round(subtotal + insurance, 2)

            updated = with_rental_totals(
                r,
                base_price=b_price,
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
            "orders": processed_rentals,
        }

    return process


def process_rentals_pure(
    rentals: Iterable[Rental],
    *,
    filter_policy: FilterPolicyFn = default_rental_filter,
    discount_policy: DiscountPolicyFn = default_duration_discount,
    insurance_policy: InsurancePolicyFn = default_insurance_fee,
) -> dict[str, Any]:
    """Прямий чистий виклик процесора оренди."""
    processor = make_rental_processor(
        filter_policy=filter_policy,
        discount_policy=discount_policy,
        insurance_policy=insurance_policy,
    )
    return processor(rentals)
