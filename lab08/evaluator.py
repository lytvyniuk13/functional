"""evaluator.py — Чисті функції обробки JSON-дерева через структурний match/case."""

from __future__ import annotations
from typing import Any, Dict, List
from model import JArray, JBool, JNull, JNumber, JObject, JString, JValue


def count_nodes(node: JValue) -> int:
    """Рекурсивний підрахунок кількості всіх вузлів у дереві через match/case."""
    match node:
        case JNull() | JBool() | JNumber() | JString():
            return 1
        case JArray(elements=elems):
            return 1 + sum(count_nodes(elem) for elem in elems)
        case JObject(fields=flds):
            return 1 + sum(count_nodes(val) for _, val in flds)


def max_depth(node: JValue) -> int:
    """Обчислення максимальної глибини вкладеності JSON-структури."""
    match node:
        case JNull() | JBool() | JNumber() | JString():
            return 1
        case JArray(elements=()):
            return 1
        case JArray(elements=elems):
            return 1 + max(max_depth(elem) for elem in elems)
        case JObject(fields=()):
            return 1
        case JObject(fields=flds):
            return 1 + max(max_depth(val) for _, val in flds)


def to_native(node: JValue) -> Any:
    """Конвертує JValue-дерево у нативні типи Python (None, bool, int/float, str, list, dict)."""
    match node:
        case JNull():
            return None
        case JBool(value=v):
            return v
        case JNumber(value=v):
            return v
        case JString(value=v):
            return v
        case JArray(elements=elems):
            return [to_native(elem) for elem in elems]
        case JObject(fields=flds):
            return {k: to_native(v) for k, v in flds}


def from_native(data: Any) -> JValue:
    """Будує незмінне JValue-дерево зі стандартних структур даних Python."""
    match data:
        case None:
            return JNull()
        case bool(v):
            return JBool(v)
        case int(v) | float(v):
            return JNumber(v)
        case str(v):
            return JString(v)
        case list(elems) | tuple(elems):
            return JArray(tuple(from_native(e) for e in elems))
        case dict(mapping):
            return JObject(
                tuple((str(k), from_native(v)) for k, v in mapping.items())
            )
        case _:
            raise TypeError(
                f"Неможливо конвертувати тип {type(data)!r} у дерево JValue"
            )