import attr
import pytest

from carriage import List, Nothing, Some
from carriage.sequence import CurrNext, CurrPrev, ValueIndex


def test_list():
    alist = List([1, 2, 3])
    assert alist == List.range(1, 4)

    def multiply_2(n):
        return n * 2

    assert alist.map(multiply_2) == List([2, 4, 6])

    def duplicate(v):
        return [v] * 2

    assert alist.flat_map(duplicate) == List([1, 1, 2, 2, 3, 3])

    assert alist.map(duplicate) == List([[1, 1], [2, 2], [3, 3]])
    assert alist.map(duplicate).flatten() == List([1, 1, 2, 2, 3, 3])


def test_access():
    alist = List.range(10, 20)
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

    emptylist = List()
    assert emptylist.first_opt() is Nothing
    assert emptylist.last_opt() is Nothing


def test_slice():
    alist = List.range(10, 20)
    assert alist[:5] == List.range(10, 15)
    assert alist[-3:] == List.range(17, 20)
    assert alist.take(5) == List.range(10, 15)
    assert alist.drop(3) == List.range(13, 20)
    assert alist.drop(10) == List()
    assert alist.drop(20) == List()
    assert alist.takeright(3) == List.range(17, 20)
    assert alist.dropright(3) == List.range(10, 17)
    assert alist.tail() == List.range(11, 20)
    assert alist.butlast() == List.range(10, 19)
    assert alist.slice(3, 5) == List.range(13, 15)
    assert alist[3:5] == List.range(13, 15)

    def less_than_15(n):
        return n < 15

    assert alist.takewhile(less_than_15) == List.range(10, 15)
    assert alist.dropwhile(less_than_15) == List.range(15, 20)


def test_zip():
    zip_index_list = List.range(10, 13).zip_index()
    assert (zip_index_list ==
            List([ValueIndex(10, 0), ValueIndex(11, 1), ValueIndex(12, 2)]))

    assert (zip_index_list.map(attr.astuple) ==
            List.range(10, 13).zip([0, 1, 2]))

    assert (List.range(10, 13).zip_longest([0, 1]) ==
            List([(10, 0), (11, 1), (12, None)]))

    assert (List.range(10, 13).zip_longest_opt([0, 1]) ==
            List([(Some(10), Some(0)), (Some(11), Some(1)), (Some(12), Nothing)]))

    assert (List.range(10, 13).zip_prev() == List(
        [CurrPrev(10, None), CurrPrev(11, 10), CurrPrev(12, 11)]))
    assert (List.range(10, 13).zip_next() == List(
        [CurrNext(10, 11), CurrNext(11, 12), CurrNext(12, None)]))
