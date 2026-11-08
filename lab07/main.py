"""main.py — Демонстраційний модуль для Варіанта №9 (Фільми та рейтинги)."""

from pathlib import Path
from core import build_movie_ranking_pipeline
from loaders import load_movies


def main() -> None:
    print("=" * 72)
    print("      ЛАБОРАТОРНА РОБОТА №7: FUNCTOOLS ТА OPERATOR (ВАРІАНТ №9)     ")
    print("=" * 72)

    # 1. Демонстрація поліморфного завантажувача @singledispatch
    print("\n[1] ТЕСТУВАННЯ ПОЛІМОРФНОГО ЗАВАНТАЖУВАЧА (load_movies):")

    # Джерело А: Об'єкт pathlib.Path (JSON)
    json_path = Path("sample_data.json")
    movies_from_json = load_movies(json_path)
    print(f"• Завантажено з Path('{json_path}'): {len(movies_from_json)} записів")

    # Джерело Б: Відкритий файловий дескриптор (CSV)
    csv_path = Path("sample_data.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        movies_from_csv = load_movies(f)
    print(f"• Завантажено з io.TextIOBase ('{csv_path}'): {len(movies_from_csv)} записів")

    # Джерело В: Сирий JSON-рядок
    raw_json_str = '[{"title": "The Godfather", "genre": "Crime", "year": "1972", "rating": "9.2", "votes": "1900000"}]'
    movies_from_str = load_movies(raw_json_str)
    print(f"• Завантажено із str (JSON-рядок): {len(movies_from_str)} записів")

    # 2. Об'єднання та запуск конвеєра
    all_raw_movies = movies_from_json + movies_from_csv + movies_from_str
    print(f"\n[2] ВИКОНАННЯ КОНВЕЄРА (Всього на вході: {len(all_raw_movies)} фільмів):")
    print("    Критерії: year >= 2000, rating >= 8.5, Top-N = 4")

    rank_pipeline = build_movie_ranking_pipeline(
        min_year=2000, min_rating=8.5, top_n=4
    )
    ranked_movies = rank_pipeline(all_raw_movies)

    print("\n[3] РЕЗУЛЬТАТИ РАНЖУВАННЯ (@total_ordering: rating ↓, votes ↓, title ↑):")
    print("-" * 72)
    print(f"{'Ранг':<5} | {'Назва':<20} | {'Жанр':<12} | {'Рік':<5} | {'Рейтинг':<8} | {'Голоси':<10}")
    print("-" * 72)

    for rank, m in enumerate(ranked_movies, start=1):
        print(
            f"{rank:<5} | {m.title:<20} | {m.genre:<12} | {m.year:<5} | "
            f"★ {m.rating:<6.1f} | {m.votes:>10,}"
        )
    print("-" * 72)
    print("=" * 72)


if __name__ == "__main__":
    main()