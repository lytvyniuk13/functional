"""models.py — Доменна модель фільму з повною підтримкою операторів порівняння."""

from functools import total_ordering


@total_ordering
class Movie:
    """Предметна сутність фільму.

    Ранжування (@total_ordering) реалізовано за трьома критеріями:
    1. rating (рейтинг за шкалою IMDb)
    2. votes (кількість голосів як тай-брейкер)
    3. title (лексикографічний порядок назви)
    """

    __slots__ = ("title", "genre", "year", "rating", "votes")

    def __init__(
        self, title: str, genre: str, year: int, rating: float, votes: int
    ) -> None:
        self.title = title
        self.genre = genre
        self.year = year
        self.rating = rating
        self.votes = votes

    def __repr__(self) -> str:
        return (
            f"Movie(title={self.title!r}, genre={self.genre!r}, "
            f"year={self.year}, rating={self.rating:.1f}, votes={self.votes})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return NotImplemented
        return (self.rating, self.votes, self.title) == (
            other.rating,
            other.votes,
            other.title,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return NotImplemented
        return (self.rating, self.votes, self.title) < (
            other.rating,
            other.votes,
            other.title,
        )