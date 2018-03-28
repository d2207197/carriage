import pytest

from carriage import List


def test_list():
    alist = List([1, 2, 3])

    def multiply_2(n):
        return n * 2

    assert alist.map(multiply_2) == List([2, 4, 6])

    def duplicate(v):
        return [v] * 2

    assert alist.flat_map(duplicate) == List([1, 1, 2, 2, 3, 3])
