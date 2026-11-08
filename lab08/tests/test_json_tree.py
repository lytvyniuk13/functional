"""tests/test_json_tree.py — Pytest-тести для перевірки ADT JSON-дерева."""

from dataclasses import FrozenInstanceError
import json
import pytest

from evaluator import count_nodes, from_native, max_depth, to_native
from model import (
    JArray,
    JBool,
    JNull,
    JNumber,
    JObject,
    JSONNodeProtocol,
    JString,
    JValue,
)
from pretty import render


# --- 1. Тести примітивних вузлів ---


def test_primitive_nodes() -> None:
    null_node = JNull()
    assert count_nodes(null_node) == 1
    assert max_depth(null_node) == 1
    assert render(null_node, mode="compact") == "null"
    assert to_native(null_node) is None

    bool_node = JBool(True)
    assert count_nodes(bool_node) == 1
    assert render(bool_node, mode="compact") == "true"
    assert to_native(bool_node) is True

    num_node = JNumber(42.5)
    assert count_nodes(num_node) == 1
    assert render(num_node, mode="compact") == "42.5"
    assert to_native(num_node) == 42.5

    str_node = JString("hello world")
    assert count_nodes(str_node) == 1
    assert render(str_node, mode="compact") == '"hello world"'
    assert to_native(str_node) == "hello world"


# --- 2. Тести масивів (JArray) ---


def test_array_nodes() -> None:
    empty_arr = JArray(())
    assert count_nodes(empty_arr) == 1
    assert max_depth(empty_arr) == 1
    assert render(empty_arr, mode="compact") == "[]"
    assert render(empty_arr, mode="pretty") == "[]"
    assert to_native(empty_arr) == []

    nested_arr = JArray((
        JNumber(1),
        JArray((JNumber(2), JNumber(3))),
        JNumber(4),
    ))
    # 1 (зовнішній масив) + 1 (число 1) + 1 (внутрішній масив) + 2 (числа 2, 3) + 1 (число 4) = 6 вузлів
    assert count_nodes(nested_arr) == 6
    assert max_depth(nested_arr) == 3
    assert render(nested_arr, mode="compact") == "[1, [2, 3], 4]"
    assert to_native(nested_arr) == [1, [2, 3], 4]


# --- 3. Тести об'єктів (JObject) ---


def test_object_nodes() -> None:
    empty_obj = JObject(())
    assert count_nodes(empty_obj) == 1
    assert max_depth(empty_obj) == 1
    assert render(empty_obj, mode="compact") == "{}"
    assert render(empty_obj, mode="pretty") == "{}"
    assert to_native(empty_obj) == {}

    complex_obj = JObject((
        ("title", JString("Lab 8")),
        ("grade", JNumber(100)),
        ("passed", JBool(True)),
        ("meta", JNull()),
        ("sub", JObject((("key", JString("value")),))),
    ))
    # 1 (корінь) + 4 (значення полів) + 1 (під-об'єкт) + 1 (значення в під-об'єкті) = 7 вузлів
    assert count_nodes(complex_obj) == 7
    assert max_depth(complex_obj) == 3

    native = to_native(complex_obj)
    assert native == {
        "title": "Lab 8",
        "grade": 100,
        "passed": True,
        "meta": None,
        "sub": {"key": "value"},
    }


# --- 4. Тест незмінності (Immutability) ---


def test_immutability() -> None:
    num_node = JNumber(10)
    with pytest.raises(FrozenInstanceError):
        num_node.value = 20  # type: ignore

    str_node = JString("const")
    with pytest.raises(FrozenInstanceError):
        str_node.value = "change"  # type: ignore


# --- 5. Тести структурного контракту Protocol ---


def test_protocol_duck_typing() -> None:
    nodes: list[JValue] = [
        JNull(),
        JBool(False),
        JNumber(10),
        JString("abc"),
        JArray(()),
        JObject(()),
    ]
    for n in nodes:
        assert isinstance(n, JSONNodeProtocol)
        assert n.node_count() >= 1
        assert n.depth() >= 1


# --- 6. Тести валідності рендерингу та roundtrip ---


def test_from_native_and_roundtrip() -> None:
    raw_data = {
        "framework": "ADT",
        "version": 3.12,
        "features": ["pattern matching", "protocols", "dataclasses"],
        "metadata": {"ready": True, "reviewer": None},
    }
    tree = from_native(raw_data)
    assert isinstance(tree, JObject)

    # Рендеримо у JSON та парсимо стандартним модулем json для перевірки відповідності
    json_compact = render(tree, mode="compact")
    assert json.loads(json_compact) == raw_data

    json_pretty = render(tree, mode="pretty")
    assert json.loads(json_pretty) == raw_data

    # Зворотне перетворення дає ідентичний словник
    assert to_native(tree) == raw_data


def test_from_native_unsupported_type() -> None:
    with pytest.raises(TypeError, match="Неможливо конвертувати тип"):
        from_native({1, 2, 3})  # set не підтримується у чистому JSON