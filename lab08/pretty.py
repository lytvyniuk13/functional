"""pretty.py — Рендеринг JSON-дерева у текстовий вигляд за допомогою match/case."""

from __future__ import annotations
import json
from model import (
    JArray,
    JBool,
    JNull,
    JNumber,
    JObject,
    JString,
    JValue,
    RenderMode,
)


def render(
    node: JValue,
    mode: RenderMode = "compact",
    indent_level: int = 0,
    indent_size: int = 2,
) -> str:
    """Генерує валідний JSON-рядок у компактному ("compact") або структурованому ("pretty") виді."""
    indent_str = " " * (indent_level * indent_size)
    next_indent_str = " " * ((indent_level + 1) * indent_size)

    match node:
        case JNull():
            return "null"
        case JBool(value=v):
            return "true" if v else "false"
        case JNumber(value=v):
            return str(v)
        case JString(value=v):
            return json.dumps(v, ensure_ascii=False)
        case JArray(elements=()):
            return "[]"
        case JArray(elements=elems):
            if mode == "compact":
                inner = ", ".join(render(e, "compact") for e in elems)
                return f"[{inner}]"
            elements_str = ",\n".join(
                f"{next_indent_str}{render(e, 'pretty', indent_level + 1, indent_size)}"
                for e in elems
            )
            return f"[\n{elements_str}\n{indent_str}]"
        case JObject(fields=()):
            return "{}"
        case JObject(fields=flds):
            if mode == "compact":
                inner = ", ".join(
                    f"{json.dumps(k, ensure_ascii=False)}: {render(v, 'compact')}"
                    for k, v in flds
                )
                return f"{{{inner}}}"
            fields_str = ",\n".join(
                f"{next_indent_str}{json.dumps(k, ensure_ascii=False)}: {render(v, 'pretty', indent_level + 1, indent_size)}"
                for k, v in flds
            )
            return f"{{\n{fields_str}\n{indent_str}}}"