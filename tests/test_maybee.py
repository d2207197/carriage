import maybee
from maybee import Just, Nothing


def test_none():
    assert maybee.none(None) is Nothing


def test_false_value():
    m = maybee.none(False)
    assert isinstance(m, Just)
    assert m.value is False
    assert m.get_or(True) is False


def test_int_value():
    m = maybee.none(30)
    assert isinstance(m, Just)
    assert m.value == 30
    assert m.get_or(0) == 30
