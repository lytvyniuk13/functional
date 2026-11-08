"""core.py — Функціональний конвеєр на базі functools.reduce, partial та operator."""

from functools import partial, reduce
from operator import itemgetter, methodcaller
from typing import Any, Callable, Dict, Iterable, List
from models import Movie

# 1. Універсальна функція конвеєра (Threading macro через reduce)
def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Послідовно пропускає значення через ланцюжок функцій: f_n(...(f_1(value)))."""
    return reduce(lambda acc, fn: fn(acc), funcs, value)


# 2. Оптимізовані гетери та трансформатори рядків із модуля operator
get_title = itemgetter("title")
get_genre = itemgetter("genre")
get_year = itemgetter("year")
get_rating = itemgetter("rating")
get_votes = itemgetter("votes")

strip_str = methodcaller("strip")
title_case = methodcaller("title")


def normalize_movie_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Чиста нормалізація полів словника без явних циклів."""
    return {
        "title": strip_str(str(get_title(raw))),
        "genre": title_case(strip_str(str(get_genre(raw)))),
        "year": int(get_year(raw)),
        "rating": float(get_rating(raw)),
        "votes": int(get_votes(raw)),
    }


def dict_to_movie(d: Dict[str, Any]) -> Movie:
    """Конвертує очищений словник у доменний об'єкт Movie."""
    return Movie(
        title=d["title"],
        genre=d["genre"],
        year=d["year"],
        rating=d["rating"],
        votes=d["votes"],
    )


def is_qualified(movie: Movie, *, min_year: int, min_rating: float) -> bool:
    """Перевірка фільму на відповідність критеріям року та рейтингу."""
    return movie.year >= min_year and movie.rating >= min_rating


# 3. Часткове застосування (functools.partial) для етапів конвеєра
map_records = lambda fn: partial(map, fn)
filter_records = lambda pred: partial(filter, pred)
take_top = lambda n: lambda it: list(it)[:n]


def build_movie_ranking_pipeline(
    min_year: int = 2000,
    min_rating: float = 8.0,
    top_n: int = 3,
) -> Callable[[List[Dict[str, Any]]], List[Movie]]:
    """Конструює функціональний конвеєр за допомогою partial та operator."""
    # Часткове застосування критеріїв фільтрації
    qualified_filter = partial(
        is_qualified, min_year=min_year, min_rating=min_rating
    )

    # Часткове застосування сортування (Movie natural ordering за спаданням)
    sort_desc = partial(sorted, reverse=True)

    def run_pipeline(raw_movies: List[Dict[str, Any]]) -> List[Movie]:
        return pipeline(
            raw_movies,
            map_records(normalize_movie_dict),
            map_records(dict_to_movie),
            filter_records(qualified_filter),
            list,
            sort_desc,
            take_top(top_n),
        )

    return run_pipeline