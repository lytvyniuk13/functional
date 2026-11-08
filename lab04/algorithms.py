"""algorithms.py — Базові рекурсивні структури: Quicksort, Дерева та Fibonacci."""

from dataclasses import dataclass
from functools import lru_cache
from random import choice
from typing import Generator, List, Optional


# --- 1. Чистий рекурсивний Quicksort ---
def quicksort(xs: List[int]) -> List[int]:
    """Рекурсивний функціональний QuickSort.

    Базовий випадок: список із 0 або 1 елемента вже відсортований.
    Рекурсивний крок: вибір pivot, розбиття на три списки та конкатенація.
    """
    if len(xs) <= 1:
        return xs[:]

    # Випадковий pivot нівелює загрозу O(n^2) для вже впорядкованих масивів
    pivot = choice(xs)
    left = [x for x in xs if x < pivot]
    mid = [x for x in xs if x == pivot]
    right = [x for x in xs if x > pivot]

    return quicksort(left) + mid + quicksort(right)


# --- 2. Бінарне дерево та обходи ---
@dataclass(slots=True)
class Node:
    """Вузол бінарного дерева."""

    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None


def preorder(t: Optional[Node]) -> Generator[int, None, None]:
    """Прямий рекурсивний обхід (Root -> Left -> Right)."""
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Optional[Node]) -> Generator[int, None, None]:
    """Центрований рекурсивний обхід (Left -> Root -> Right)."""
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Optional[Node]) -> Generator[int, None, None]:
    """Зворотний рекурсивний обхід (Left -> Right -> Root)."""
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Optional[Node]) -> List[int]:
    """Ітеративний обхід дерева за рівнями (BFS)."""
    if not t:
        return []
    from collections import deque

    q, out = deque([t]), []
    while q:
        n = q.popleft()
        out.append(n.key)
        if n.left:
            q.append(n.left)
        if n.right:
            q.append(n.right)
    return out


def dfs_preorder_iter(t: Optional[Node]) -> List[int]:
    """Ітеративний прямий обхід (DFS) з явним стеком."""
    if not t:
        return []
    stack, out = [t], []
    while stack:
        n = stack.pop()
        out.append(n.key)
        # Спочатку кладемо правий, щоб лівий витягнувся першим
        if n.right:
            stack.append(n.right)
        if n.left:
            stack.append(n.left)
    return out


# --- 3. Fibonacci з мемоізацією та ітеративний аналог ---
@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Рекурсивний розрахунок чисел Фібоначчі з кешуванням lru_cache."""
    if n < 0:
        raise ValueError("n має бути невід'ємним числом")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_iter(n: int) -> int:
    """Ітеративний розрахунок Фібоначчі зі складністю O(n) за часом та O(1) за пам'яттю."""
    if n < 0:
        raise ValueError("n має бути невід'ємним числом")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a