"""app.py — Демонстраційний модуль (Imperative Shell)."""

import time
from algorithms import fib, fib_iter, quicksort
from maze import (
    find_path_bfs,
    find_path_dfs_iterative,
    find_path_dfs_recursive,
    make_path_counter,
    render_maze_with_path,
)


def main() -> None:
    print("=" * 66)
    print("      ЛАБОРАТОРНА РОБОТА №4: РЕКУРСІЯ ТА МЕМОІЗАЦІЯ         ")
    print("               ВАРІАНТ №9: ПОШУК У ЛАБІРИНТІ                ")
    print("=" * 66)

    # 1. Тестова карта лабіринту (S — старт, E — фініш, # — стіна, . — коридор)
    maze = (
        "S...#....#",
        ".#..#..#..",
        ".#.....#..",
        "...###.#..",
        ".#.#...#..",
        "...#.#...E",
    )
    start = (0, 0)
    target = (5, 9)

    print("\n[1] ПОЧАТКОВИЙ ЛАБІРИНТ:")
    for row in maze:
        print(f"  {row}")

    # Рекурсивний DFS
    t0 = time.perf_counter()
    dfs_rec_path = find_path_dfs_recursive(maze, start, target)
    t_dfs_rec = time.perf_counter() - t0

    # Ітеративний DFS
    t0 = time.perf_counter()
    dfs_iter_path = find_path_dfs_iterative(maze, start, target)
    t_dfs_iter = time.perf_counter() - t0

    # Ітеративний BFS
    t0 = time.perf_counter()
    bfs_path = find_path_bfs(maze, start, target)
    t_bfs = time.perf_counter() - t0

    print("\n[2] РЕЗУЛЬТАТИ ПОШУКУ МАРШРУТУ:")
    print(
        f"• Рекурсивний DFS: довжина = {len(dfs_rec_path) if dfs_rec_path else 0} кроків | час = {t_dfs_rec * 1e6:.2f} мкс"
    )
    print(
        f"• Ітеративний DFS: довжина = {len(dfs_iter_path) if dfs_iter_path else 0} кроків | час = {t_dfs_iter * 1e6:.2f} мкс"
    )
    print(
        f"• Ітеративний BFS: довжина = {len(bfs_path) if bfs_path else 0} кроків (НАЙКОРОТШИЙ) | час = {t_bfs * 1e6:.2f} мкс"
    )

    print("\n[3] ВІЗУАЛІЗАЦІЯ НАЙКОРОТШОГО ШЛЯХУ (BFS):")
    print(render_maze_with_path(maze, bfs_path))

    # Демонстрація memoized підрахунку шляхів
    print("\n[4] ДИСПЕТЧЕР ДИНАМІЧНОГО ПРОГРАМУВАННЯ (lru_cache):")
    sub_maze = (
        "....",
        ".#..",
        "....",
        "..#E",
    )
    counter = make_path_counter(sub_maze, target=(3, 3))
    total_paths = counter(0, 0)
    print(f"• Унікальних шляхів (Right/Down) у підлабіринті: {total_paths}")
    print(f"• Статистика кешу: {counter.cache_info()}")

    # Демонстрація базових алгоритмів
    print("\n[5] БАЗОВІ АЛГОРИТМИ:")
    sample_list = [64, 34, 25, 12, 22, 11, 90]
    print(f"• Pure Quicksort: {quicksort(sample_list)}")

    fib.cache_clear()
    fib_val = fib(35)
    print(
        f"• Fib(35) = {fib_val} (збігається з fib_iter: {fib_val == fib_iter(35)})"
    )
    print(f"• Fib Cache Info: {fib.cache_info()}")
    print("=" * 66)


if __name__ == "__main__":
    main()