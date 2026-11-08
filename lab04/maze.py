"""maze.py — Розв'язання задачі про лабіринт (Варіант №9).

Містить чистий рекурсивний DFS, ітеративні DFS та BFS, а також мемоізований
підрахунок можливих маршрутів.
"""

from collections import deque
from functools import lru_cache
from typing import Callable, FrozenSet, List, Optional, Set, Tuple

Point = Tuple[int, int]
# Незмінна матриця лабіринту: кортеж текстових рядків
MazeGrid = Tuple[str, ...]


def is_valid_move(grid: MazeGrid, r: int, c: int) -> bool:
    """Перевіряє, чи координата лежить у межах сітки та не є стіною '#'."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    return 0 <= r < rows and 0 <= c < cols and grid[r][c] != "#"


def find_path_dfs_recursive(
    grid: MazeGrid,
    current: Point,
    target: Point,
    visited: Optional[FrozenSet[Point]] = None,
) -> Optional[Tuple[Point, ...]]:
    """Чистий рекурсивний пошук у глибину (DFS).

    Базовий випадок:
    1. Поточна координата невалідна або вже відвідана -> повертаємо None.
    2. Поточна точка дорівнює цільовій (target) -> знайдено вихід, повертаємо (current,).

    Рекурсивний крок:
    Додаємо current до незмінної множини visited та рекурсивно перевіряємо
    4 сусідні клітинки (Вгору, Вправо, Вниз, Вліво).
    """
    if visited is None:
        visited = frozenset()

    r, c = current
    if not is_valid_move(grid, r, c) or current in visited:
        return None

    if current == target:
        return (current,)

    new_visited = visited | frozenset({current})

    # Напрямки: Вгору, Вправо, Вниз, Вліво
    directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    for dr, dc in directions:
        next_point = (r + dr, c + dc)
        path = find_path_dfs_recursive(grid, next_point, target, new_visited)
        if path is not None:
            # Зворотний крок: чиста композиція кортежу без мутації
            return (current,) + path

    return None


def find_path_dfs_iterative(
    grid: MazeGrid, start: Point, target: Point
) -> Optional[Tuple[Point, ...]]:
    """Ітеративний DFS на власному стеку (LIFO).

    Безпечний щодо переповнення стеку викликів інтерпретатора.
    """
    if not is_valid_move(grid, start[0], start[1]) or not is_valid_move(
        grid, target[0], target[1]
    ):
        return None

    stack: List[Tuple[Point, Tuple[Point, ...]]] = [(start, (start,))]
    visited: Set[Point] = {start}

    while stack:
        curr, path = stack.pop()
        if curr == target:
            return path

        r, c = curr
        # Зворотний порядок напрямків, щоб першим оброблявся верх/право
        for dr, dc in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            nxt = (r + dr, c + dc)
            if is_valid_move(grid, nxt[0], nxt[1]) and nxt not in visited:
                visited.add(nxt)
                stack.append((nxt, path + (nxt,)))

    return None


def find_path_bfs(
    grid: MazeGrid, start: Point, target: Point
) -> Optional[Tuple[Point, ...]]:
    """Ітеративний пошук у ширину (BFS) на базі collections.deque (FIFO).

    Гарантує знаходження найкоротшого шляху (мінімальної кількості кроків).
    """
    if not is_valid_move(grid, start[0], start[1]) or not is_valid_move(
        grid, target[0], target[1]
    ):
        return None

    queue: deque[Tuple[Point, Tuple[Point, ...]]] = deque([(start, (start,))])
    visited: Set[Point] = {start}

    while queue:
        curr, path = queue.popleft()
        if curr == target:
            return path

        r, c = curr
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nxt = (r + dr, c + dc)
            if is_valid_move(grid, nxt[0], nxt[1]) and nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + (nxt,)))

    return None


def make_path_counter(
    grid: MazeGrid, target: Point
) -> Callable[[int, int], int]:
    """Фабрика для створення мемоізованої функції підрахунку кількості шляхів.

    Демонстрація functools.lru_cache у динамічному програмуванні на сітці.
    """

    @lru_cache(maxsize=None)
    def count_paths(r: int, c: int) -> int:
        # Базові випадки:
        if not is_valid_move(grid, r, c):
            return 0
        if (r, c) == target:
            return 1

        # Рекурсивний крок: сума шляхів при русі вправо та вниз
        return count_paths(r + 1, c) + count_paths(r, c + 1)

    return count_paths


def render_maze_with_path(
    grid: MazeGrid, path: Optional[Tuple[Point, ...]]
) -> str:
    """I/O функція для візуалізації пройденого маршруту символами '*'."""
    path_set = set(path) if path else set()
    rendered_lines = []

    for r_idx, row in enumerate(grid):
        line = []
        for c_idx, char in enumerate(row):
            pt = (r_idx, c_idx)
            if pt in path_set and char not in {"S", "E"}:
                line.append("*")
            else:
                line.append(char)
        rendered_lines.append("".join(line))

    return "\n".join(rendered_lines)