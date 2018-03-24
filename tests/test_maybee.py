import pytest

from maybee import Just, Maybe, Nothing, NothingError, maybe


def test_none():
    m = maybe(None)
    assert m is Nothing
    with pytest.raises(NothingError):
        m.get()

    assert m.get_or(0) == 0
    assert m.get_or(None) is None
    assert m.get_or(False) is False
    assert m.get_or(True) is True
    assert m.get_or("A string") == "A string"


def test_non_none():
    check_just_value(maybe(30), 30)
    check_just_value(maybe(False), False)
    check_just_value(maybe("Hello"), "Hello")
    d = {'john': 50, 'doe': 10}
    check_just_value(maybe(d), d)


def check_just_value(just, value):
    assert isinstance(just, Just)
    assert just.get() == value
    assert just.get_or(None) == value
    assert just.get_or("Yo") == value


def test_get_attr():
    class Clz:
        def __init__(self, data):
            self.data = data

        def get_data(self):
            return self.data
    assert maybe(Clz(30)).get_data().get() == 30
    assert maybe(Clz(30)).get_data().v == 30


def test_eq_ne_comparator():
    just_hello = maybe("hello")
    just_hello_2 = maybe("hello")
    just_world = maybe("world")

    assert just_hello == just_hello_2
    with pytest.raises(TypeError):
        assert just_hello == "hello"

    assert just_hello != just_world
    with pytest.raises(TypeError):
        assert just_hello != "world"


def test_gt_lt_ge_le_comparator():
    just_100 = maybe(100)
    just_100_2 = maybe(100)
    just_200 = maybe(200)
    assert just_100 < just_200
    assert just_200 > just_100
    assert just_100 <= just_200
    assert just_200 >= just_100
    assert just_100 <= just_100_2
    assert just_100 >= just_100_2


def test_function():
    value = 50
    m = Maybe.except_call(lambda: value)
    assert isinstance(m, Just)
    assert m.get() == value
    assert m.get_or(None) == value
    assert m.get_or("Yo") == value
