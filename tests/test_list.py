import pytest

from carriage import List, Nothing, Some


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
