"""loaders.py — Поліморфний API завантаження даних через functools.singledispatch."""

import csv
from functools import singledispatch
import io
import json
from pathlib import Path
from typing import Any, Dict, List


@singledispatch
def load_movies(src: Any) -> List[Dict[str, Any]]:
    """Базова генерична функція завантаження списку фільмів.

    Викидає TypeError, якщо тип джерела не зареєстровано.
    """
    raise TypeError(f"Непідтримуваний тип джерела для завантаження: {type(src)!r}")


def _parse_csv_text(text: str) -> List[Dict[str, Any]]:
    """Парсить текст у форматі CSV у список словників."""
    reader = csv.DictReader(io.StringIO(text.strip()))
    return [dict(row) for row in reader]


@load_movies.register
def _(src: str) -> List[Dict[str, Any]]:
    """Обробка рядка: сирий JSON, сирий CSV або шлях до файлу."""
    s = src.strip()
    if s.startswith("[") or s.startswith("{"):
        parsed = json.loads(s)
        return [parsed] if isinstance(parsed, dict) else parsed

    # Якщо передано шлях до файлу у вигляді str
    path = Path(s)
    if path.is_file() or path.suffix.lower() in {".json", ".csv"}:
        return load_movies(path)

    # Якщо це вміст CSV безпосередньо у рядку
    if "title" in s and "," in s:
        return _parse_csv_text(s)

    raise ValueError(f"Неможливо інтерпретувати рядок як дані або шлях: {src[:50]}")


@load_movies.register
def _(src: Path) -> List[Dict[str, Any]]:
    """Обробка об'єкта pathlib.Path (підтримка .json та .csv)."""
    text = src.read_text(encoding="utf-8")
    if src.suffix.lower() == ".csv":
        return _parse_csv_text(text)
    parsed = json.loads(text)
    return [parsed] if isinstance(parsed, dict) else parsed


@load_movies.register
def _(src: io.TextIOBase) -> List[Dict[str, Any]]:
    """Обробка відкритого текстового файлового дескриптора."""
    content = src.read().strip()
    if content.startswith("[") or content.startswith("{"):
        parsed = json.loads(content)
        return [parsed] if isinstance(parsed, dict) else parsed
    return _parse_csv_text(content)


@load_movies.register
def _(src: list) -> List[Dict[str, Any]]:
    """Обробка вже завантаженого в пам'ять списку."""
    if src and not isinstance(src[0], dict):
        raise ValueError("Очікується список словників (list of dicts)")
    return src