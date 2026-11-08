"""tests/test_lab07.py — Комплексні pytest-тести для лабораторної роботи №7."""

import io
import json
from pathlib import Path
import tempfile
from typing import Any, Dict, List
import pytest

from core import (
    build_movie_ranking_pipeline,
    get_title,
    normalize_movie_dict,
    pipeline,
    strip_str,
    title_case,
)
from loaders import load_movies
from models import Movie


@pytest.fixture
def sample_raw_movies() -> List[Dict[str, Any]]:
    return [
        {
            "title": "  Inception  ",
            "genre": "sci-fi",
            "year": "2010",
            "rating": "8.8",
            "votes": "2400000",
        },
        {
            "title": "The Matrix",
            "genre": "Sci-Fi",
            "year": "1999",
            "rating": "8.7",
            "votes": "1900000",
        },  # year < 2000
        {
            "title": "Interstellar",
            "genre": "Adventure",
            "year": "2014",
            "rating": "8.7",
            "votes": "1900000",
        },
        {
            "title": "The Dark Knight",
            "genre": "Action",
            "year": "2008",
            "rating": "9.0",
            "votes": "2700000",
        },
        {
            "title": "Low Rated",
            "genre": "Drama",
            "year": "2020",
            "rating": "6.5",
            "votes": "50000",
        },  # rating < 8.0
    ]


# --- 1. Тести функції pipeline (functools.reduce) ---


def test_pipeline_reduce_execution() -> None:
    # f(x) = ((x + 3) * 2) - 1
    result = pipeline(5, lambda x: x + 3, lambda x: x * 2, lambda x: x - 1)
    assert result == 15


# --- 2. Тести моделі Movie та декоратора @total_ordering ---


def test_movie_total_ordering() -> None:
    m1 = Movie("Alpha", "Action", 2020, 8.5, 1000)
    m2 = Movie("Beta", "Action", 2020, 8.5, 2000)  # більше голосів при рівному рейтингу
    m3 = Movie("Gamma", "Action", 2020, 9.0, 500)   # вищий рейтинг
    m4 = Movie("Alpha", "Action", 2020, 8.5, 1000)  # ідентичний m1

    # __eq__
    assert m1 == m4
    assert m1 != m2
    assert not (m1 == "Not a movie")

    # __lt__, __le__, __gt__, __ge__
    assert m1 < m2
    assert m1 <= m2
    assert m2 > m1
    assert m2 >= m1
    assert m3 > m2
    assert m3 >= m2

    # max / min / sorted
    movies = [m2, m3, m1]
    assert max(movies) is m3
    assert min(movies) is m1
    assert sorted(movies) == [m1, m2, m3]

    # Перевірка винятків при порівнянні з чужим типом
    with pytest.raises(TypeError):
        _ = m1 < 100


# --- 3. Тести утиліт модуля operator ---


def test_operator_utilities() -> None:
    row = {"title": "  dune: part two  ", "genre": " sci-fi "}
    assert get_title(row) == "  dune: part two  "
    assert strip_str(get_title(row)) == "dune: part two"
    assert title_case(strip_str(row["genre"])) == "Sci-Fi"

    normalized = normalize_movie_dict({
        "title": "  Tenet ",
        "genre": "action",
        "year": "2020",
        "rating": "7.3",
        "votes": "500000",
    })
    assert normalized == {
        "title": "Tenet",
        "genre": "Action",
        "year": 2020,
        "rating": 7.3,
        "votes": 500000,
    }


# --- 4. Тести конвеєра фільтрації та ранжування ---


def test_movie_ranking_pipeline(sample_raw_movies: List[Dict[str, Any]]) -> None:
    pipeline_fn = build_movie_ranking_pipeline(
        min_year=2000, min_rating=8.0, top_n=2
    )
    ranked = pipeline_fn(sample_raw_movies)

    assert len(ranked) == 2
    # Ранг 1: The Dark Knight (9.0, 2.7M)
    assert ranked[0].title == "The Dark Knight"
    assert ranked[0].rating == 9.0
    # Ранг 2: Inception (8.8, 2.4M)
    assert ranked[1].title == "Inception"
    assert ranked[1].rating == 8.8


# --- 5. Тести поліморфного завантажувача @singledispatch ---


def test_singledispatch_loaders() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "movies.json"
        csv_file = Path(tmpdir) / "movies.csv"

        test_data = [
            {"title": "Dune", "genre": "Sci-Fi", "year": "2021", "rating": "8.0", "votes": "700000"}
        ]
        json_file.write_text(json.dumps(test_data), encoding="utf-8")
        csv_file.write_text(
            "title,genre,year,rating,votes\nDune,Sci-Fi,2021,8.0,700000\n",
            encoding="utf-8",
        )

        # 1. JSON string
        assert len(load_movies(json.dumps(test_data))) == 1
        # 2. str path (JSON)
        assert len(load_movies(str(json_file))) == 1
        # 3. str path (CSV)
        assert len(load_movies(str(csv_file))) == 1
        # 4. Path (JSON)
        assert len(load_movies(json_file)) == 1
        # 5. Path (CSV)
        assert len(load_movies(csv_file)) == 1
        # 6. Відкритий файловий дескриптор
        with open(json_file, encoding="utf-8") as f:
            assert len(load_movies(f)) == 1
        # 7. Список словників
        assert len(load_movies(test_data)) == 1

        # Непідтримуваний тип -> TypeError
        with pytest.raises(TypeError):
            load_movies(99999)