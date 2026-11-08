"""tests/test_algorithms.py — Тести Quicksort, обходів дерев та memoized Fibonacci."""

import random
from algorithms import (
    Node,
    bfs_level_order,
    dfs_preorder_iter,
    fib,
    fib_iter,
    inorder,
    postorder,
    preorder,
    quicksort,
)
import pytest


def test_quicksort_edge_cases() -> None:
    assert quicksort([]) == []
    assert quicksort([42]) == [42]
    assert quicksort([5, 1, 4, 2, 8]) == [1, 2, 4, 5, 8]
    assert quicksort([2, 2, 2, 2]) == [2, 2, 2, 2]


def test_quicksort_random_parity() -> None:
    data = [random.randint(-1000, 1000) for _ in range(300)]
    assert quicksort(data) == sorted(data)


def test_binary_tree_traversals() -> None:
    #      4
    #     / \
    #    2   6
    #   / \   \
    #  1   3   7
    tree = Node(
        4, left=Node(2, Node(1), Node(3)), right=Node(6, None, Node(7))
    )

    assert list(preorder(tree)) == [4, 2, 1, 3, 6, 7]
    assert list(inorder(tree)) == [1, 2, 3, 4, 6, 7]
    assert list(postorder(tree)) == [1, 3, 2, 7, 6, 4]
    assert bfs_level_order(tree) == [4, 2, 6, 1, 3, 7]
    assert dfs_preorder_iter(tree) == [4, 2, 1, 3, 6, 7]


def test_fibonacci_memoization_parity() -> None:
    fib.cache_clear()
    assert [fib(i) for i in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    for n in range(40):
        assert fib(n) == fib_iter(n)

    info = fib.cache_info()
    assert info.hits > 0


def test_fibonacci_invalid_argument() -> None:
    with pytest.raises(ValueError):
        fib(-5)