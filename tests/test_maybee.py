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
    maybe(Clz(30)).get_data() == 30


def test_function():
    value = 50
    m = Maybe.except_call(lambda: value)
    assert isinstance(m, Just)
    assert m.get() == value
    assert m.get_or(None) == value
    assert m.get_or("Yo") == value
