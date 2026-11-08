"""model.py — Алгебраїчний тип даних (ADT) для JSON-подібного дерева (Варіант №9).

Включає незмінні dataclass-вузли, рекурсивний TypeAlias JValue,
Literal для режимів форматування та Protocol для структурного контракту.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Protocol, Tuple, TypeAlias, Union, runtime_checkable

# 1. Literal для строгого обмеження режимів рендерингу
RenderMode: TypeAlias = Literal["compact", "pretty"]


# 2. Структурний контракт Protocol (duck typing із перевіркою mypy)
@runtime_checkable
class JSONNodeProtocol(Protocol):
    """Протокол, що гарантує наявність метрик кількості вузлів та глибини."""

    def node_count(self) -> int: ...
    def depth(self) -> int: ...


# 3. Базові вузли дерева як незмінні сутності (frozen=True, slots=True)
@dataclass(frozen=True, slots=True)
class JNull:
    """Представлення значення null."""

    def node_count(self) -> int:
        return 1

    def depth(self) -> int:
        return 1


@dataclass(frozen=True, slots=True)
class JBool:
    """Представлення булевого значення (true/false)."""

    value: bool

    def node_count(self) -> int:
        return 1

    def depth(self) -> int:
        return 1


@dataclass(frozen=True, slots=True)
class JNumber:
    """Представлення числового значення (ціле або дробове)."""

    value: int | float

    def node_count(self) -> int:
        return 1

    def depth(self) -> int:
        return 1


@dataclass(frozen=True, slots=True)
class JString:
    """Представлення текстового рядка."""

    value: str

    def node_count(self) -> int:
        return 1

    def depth(self) -> int:
        return 1


@dataclass(frozen=True, slots=True)
class JArray:
    """Представлення JSON-масиву через незмінний кортеж елементів."""

    elements: Tuple[JValue, ...]

    def node_count(self) -> int:
        return 1 + sum(e.node_count() for e in self.elements)

    def depth(self) -> int:
        if not self.elements:
            return 1
        return 1 + max(e.depth() for e in self.elements)


@dataclass(frozen=True, slots=True)
class JObject:
    """Представлення JSON-об'єкта через кортеж пар (ключ, значення)."""

    fields: Tuple[Tuple[str, JValue], ...]

    def node_count(self) -> int:
        return 1 + sum(val.node_count() for _, val in self.fields)

    def depth(self) -> int:
        if not self.fields:
            return 1
        return 1 + max(val.depth() for _, val in self.fields)


# 4. Рекурсивний сумарний тип (Sum Type / Union)
JValue: TypeAlias = Union[JNull, JBool, JNumber, JString, JArray, JObject]