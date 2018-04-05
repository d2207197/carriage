import attr
import pytest

from carriage import Array, Nothing, Some
from carriage.types import CurrNext, CurrPrev, ValueIndex


def test_init():
    alist = Array([1, 2, 3])
    assert alist == Array.range(1, 4)


def test_access():
    alist = Array.range(10, 20)
    assert alist[9] == 19
    assert alist[-1] == 19
    assert alist[-10] == 10
    with pytest.raises(IndexError):
        alist[10]
    with pytest.raises(IndexError):
        alist[-11]

    assert alist.get(3) == 13
    assert alist.get(10) is None
    assert alist.get(3, 0) == 13
    assert alist.get(10, 0) == 0
    assert alist.get_opt(3) == Some(13)
    assert alist.get_opt(-2) == Some(18)
    assert alist.get_opt(-10) == Some(10)
    assert alist.get_opt(-11) is Nothing
    assert alist.get_opt(10) is Nothing

    assert alist.first() == 10
    assert alist.second() == 11
    assert alist.last() == 19
    assert alist.first_opt() == Some(10)
    assert alist.last_opt() == Some(19)

    emptylist = Array()
    assert emptylist.first_opt() is Nothing
    assert emptylist.last_opt() is Nothing


def test_slice():
    alist = Array.range(10, 20)
    assert alist[:5] == Array.range(10, 15)
    assert alist[-3:] == Array.range(17, 20)
    assert alist.take(5) == Array.range(10, 15)
    assert alist.drop(3) == Array.range(13, 20)
    assert alist.drop(10) == Array()
    assert alist.drop(20) == Array()
    assert alist.takeright(3) == Array.range(17, 20)
    assert alist.dropright(3) == Array.range(10, 17)
    assert alist.tail() == Array.range(11, 20)
    assert alist.butlast() == Array.range(10, 19)
    assert alist.slice(3, 5) == Array.range(13, 15)
    assert alist[3:5] == Array.range(13, 15)

    def less_than_15(n):
        return n < 15

    assert alist.takewhile(less_than_15) == Array.range(10, 15)
    assert alist.dropwhile(less_than_15) == Array.range(15, 20)


def test_zip():
    zip_index_list = Array.range(10, 13).zip_index()
    assert (zip_index_list ==
            Array([ValueIndex(10, 0), ValueIndex(11, 1), ValueIndex(12, 2)]))

    assert (zip_index_list.map(attr.astuple) ==
            Array.range(10, 13).zip([0, 1, 2]))

    assert (Array.range(10, 13).zip_longest([0, 1]) ==
            Array([(10, 0), (11, 1), (12, None)]))

    assert (Array.range(10, 13).zip_longest_opt([0, 1]) ==
            Array([(Some(10), Some(0)), (Some(11), Some(1)),
                   (Some(12), Nothing)]))

    assert (Array.range(10, 13).zip_prev() == Array(
        [CurrPrev(10, None), CurrPrev(11, 10), CurrPrev(12, 11)]))
    assert (Array.range(10, 13).zip_next() == Array(
        [CurrNext(10, 11), CurrNext(11, 12), CurrNext(12, None)]))


def test_basic_transform():
    alist = Array([1, 2, 3])

    def multiply_2(n):
        return n * 2

    assert alist.map(multiply_2) == Array([2, 4, 6])

    def duplicate(v):
        return [v] * 2

    assert alist.flat_map(duplicate) == Array([1, 1, 2, 2, 3, 3])

    assert alist.map(duplicate) == Array([[1, 1], [2, 2], [3, 3]])
    assert alist.map(duplicate).flatten() == Array([1, 1, 2, 2, 3, 3])

    alist = Array.range(10, 15).zip(Array.range(5, 10))
    assert alist.starmap(lambda a, b: a - b) == Array([5] * 5)

    alist = Array.range(5)

    def is_even(n):
        return n % 2 == 0

    assert alist.filter(is_even) == Array([0, 2, 4])


def test_reorder():
    alist = Array.range(5)
    assert alist.reverse() is alist
    assert alist == Array([4, 3, 2, 1, 0])

    alist = Array.range(5)
    assert alist.reversed() is not alist
    assert alist.reversed() == Array([4, 3, 2, 1, 0])

    alist = Array([5, 2, 3, 4, 1])
    assert alist.sort(key=lambda n: -n) is alist
    assert alist == Array([5, 4, 3, 2, 1])

    alist = Array([5, 2, 3, 4, 1])
    assert alist.sorted(key=lambda n: -n) is not alist
    assert alist.sorted(key=lambda n: -n) == Array([5, 4, 3, 2, 1])


def test_extend():
    alist = Array.range(5)
    assert alist.extend([5, 6]) is alist
    assert alist == Array([0, 1, 2, 3, 4, 5, 6])

    alist = Array.range(5)
    assert alist.extended([5, 6]) is not alist
    assert alist.extended([5, 6]) == Array([0, 1, 2, 3, 4, 5, 6])


def test_append():
    alist = Array.range(5)
    assert alist.append(5) is alist
    assert alist == Array([0, 1, 2, 3, 4, 5])

    alist = Array.range(5)
    assert alist.appended(5) is not alist
    assert alist.appended(5) == Array([0, 1, 2, 3, 4, 5])


def test_distincted():
    alist = Array([3, 2, 2, 1, 5, 1, 7])
    assert alist.distincted() == Array([3, 2, 1, 5, 7])


def test_combinatoric():
    alist = Array.range(3)
    assert alist.product(repeat=1) == Array([(0,), (1,), (2,)])
    assert alist.product(repeat=2) == Array([(0, 0), (0, 1), (0, 2),
                                             (1, 0), (1, 1), (1, 2),
                                             (2, 0), (2, 1), (2, 2),
                                             ])
    assert alist.product([0, 1, 2]) == Array([(0, 0), (0, 1), (0, 2),
                                              (1, 0), (1, 1), (1, 2),
                                              (2, 0), (2, 1), (2, 2),
                                              ])
