"""tests/test_maze.py — Набір pytest-тестів для перевірки алгоритмів лабіринту."""

from typing import Tuple
import pytest
from maze import (
    find_path_bfs,
    find_path_dfs_iterative,
    find_path_dfs_recursive,
    make_path_counter,
)


@pytest.fixture
def sample_maze() -> Tuple[str, ...]:
    return (
        "S...#",
        ".#...",
        ".#.#.",
        "...#E",
    )


def test_dfs_recursive_finds_valid_path(sample_maze: Tuple[str, ...]) -> None:
    start = (0, 0)
    end = (3, 4)
    path = find_path_dfs_recursive(sample_maze, start, end)

    assert path is not None
    assert path[0] == start
    assert path[-1] == end

    # Кожен крок має бути строго сусідньою клітинкою (Мангеттенська відстань = 1)
    for p1, p2 in zip(path[:-1], path[1:]):
        dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        assert dist == 1


def test_dfs_unreachable_target() -> None:
    blocked_maze = (
        "S###",
        "####",
        "###E",
    )
    path = find_path_dfs_recursive(blocked_maze, (0, 0), (2, 3))
    assert path is None


def test_no_mutation_of_input_grid(sample_maze: Tuple[str, ...]) -> None:
    original = tuple(sample_maze)
    _ = find_path_dfs_recursive(sample_maze, (0, 0), (3, 4))
    assert sample_maze == original


def test_bfs_guarantees_shortest_path() -> None:
    # Лабіринт із двома варіантами: довгим обхідним та прямим коротким
    loop_maze = (
        "S.....",
        ".###..",
        ".....E",
    )
    dfs_p = find_path_dfs_recursive(loop_maze, (0, 0), (2, 5))
    bfs_p = find_path_bfs(loop_maze, (0, 0), (2, 5))

    assert dfs_p is not None
    assert bfs_p is not None
    # BFS завжди знаходить шлях меншої або рівної довжини
    assert len(bfs_p) <= len(dfs_p)


def test_iterative_dfs_parity(sample_maze: Tuple[str, ...]) -> None:
    start = (0, 0)
    end = (3, 4)
    path_iter = find_path_dfs_iterative(sample_maze, start, end)

    assert path_iter is not None
    assert path_iter[0] == start
    assert path_iter[-1] == end


def test_memoized_path_counter() -> None:
    sub_grid = (
        "...",
        ".#.",
        "...",
    )
    count_fn = make_path_counter(sub_grid, (2, 2))
    total_paths = count_fn(0, 0)

    assert total_paths == 2
    info = count_fn.cache_info()
    assert info.hits > 0

    count_fn.cache_clear()
    assert count_fn.cache_info().currsize == 0