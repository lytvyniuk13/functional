"""main.py — Демонстраційний модуль для Варіанта №9 (JSON-подібне дерево)."""

from evaluator import count_nodes, from_native, max_depth, to_native
from model import (
    JArray,
    JBool,
    JNull,
    JNumber,
    JObject,
    JSONNodeProtocol,
    JString,
)
from pretty import render


def main() -> None:
    print("=" * 68)
    print("     ЛАБОРАТОРНА РОБОТА №8: АЛГЕБРАЇЧНІ ТИПИ ДАНИХ (ADT)     ")
    print("               ВАРІАНТ №9: JSON-ПОДІБНЕ ДЕРЕВО               ")
    print("=" * 68)

    # 1. Ручна збірка вкладеного ADT-дерева
    ast = JObject(
        (
            ("project", JString("Object Location Tracker")),
            ("version", JNumber(2.1)),
            ("active", JBool(True)),
            ("author", JNull()),
            (
                "stack",
                JArray((JString("Go"), JString("PostgreSQL"), JString("Pin"))),
            ),
            (
                "config",
                JObject(
                    (
                        ("city", JString("Lviv")),
                        ("max_connections", JNumber(50)),
                    )
                ),
            ),
        )
    )

    print("\n[1] АНАЛІЗ СТРУКТУРИ ДЕРЕВА:")
    total_nodes = count_nodes(ast)
    depth = max_depth(ast)
    print(f"• Загальна кількість вузлів (count_nodes): {total_nodes}")
    print(f"• Максимальна глибина (max_depth):         {depth}")

    # 2. Перевірка структурного контракту Protocol
    print("\n[2] ПЕРЕВІРКА PROTOCOL (duck typing):")
    is_proto = isinstance(ast, JSONNodeProtocol)
    print(f"• Об'єкт реалізує JSONNodeProtocol: {is_proto}")
    print(f"• Виклик методу через Protocol: ast.node_count() -> {ast.node_count()}")

    # 3. Рендеринг у режимах Literal["compact", "pretty"]
    print("\n[3] РЕНДЕРИНГ ДЕРЕВА (mode='compact'):")
    print(render(ast, mode="compact"))

    print("\n[4] РЕНДЕРИНГ ДЕРЕВА (mode='pretty'):")
    print(render(ast, mode="pretty"))

    # 4. Конвертація у нативний Python dict
    print("\n[5] КОНВЕРТАЦІЯ to_native():")
    native_dict = to_native(ast)
    print(native_dict)

    # 5. Roundtrip конвертація from_native
    print("\n[6] ЗВОРОТНА КОНВЕРТАЦІЯ from_native() -> ПЕРЕВІРКА РІВНОСТІ:")
    reconstructed = from_native(native_dict)
    print(f"• Відновлене дерево дорівнює оригіналу: {reconstructed == ast}")
    print("=" * 68)


if __name__ == "__main__":
    main()