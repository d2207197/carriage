import pytest

from maybee import Nothing, NothingError, Optional, Some


def test_value_noneable_init():
    nothing = Optional.value_noneable(None)
    assert nothing is Nothing
    with pytest.raises(NothingError):
        Nothing.value

    some = Optional.value_noneable(30)
    assert type(some) is Some
    assert some.value == 30

    some = Optional.value_noneable("hello")
    assert type(some) is Some
    assert some.value == "hello"

    adict = {'apple': 1, 'orange': 2}
    some = Optional.value_noneable(adict)
    assert type(some) is Some
    assert some.value == {'apple': 1, 'orange': 2}
    assert some.value is adict


def test_call_exceptable():
    def raise_exception():
        raise Exception
    assert Optional.call_exceptable(raise_exception) is Nothing


def test_some_value():
    assert Some(30).value == 30
    assert Some(None).value is None
    assert Some(None).value is None
    assert Some([1, 2, 3]).value == [1, 2, 3]
    alist = [4, 5, 6]
    assert Some(alist).value is alist
    assert Some({'apple': 1, 'orange': 2}).value == {'apple': 1, 'orange': 2}
    adict = {'apple': 1, 'orange': 2}
    assert Some(adict).value is adict


def test_get_or():
    assert Some(30).get_or(None) == 30
    assert Some(None).get_or(None) is None
    assert Some(None).get_or(True) is None
    assert Some([1, 2, 3]).get_or(True) == [1, 2, 3]

    assert Nothing.get_or(0) == 0
    assert Nothing.get_or(None) is None
    assert Nothing.get_or(False) is False
    assert Nothing.get_or(True) is True
    assert Nothing.get_or("A string") == "A string"


def test_map():
    def multiply_2(n):
        return n * 2
    res = Some(100).map(multiply_2)
    assert res.value == 200

    res = Nothing.map(multiply_2)
    assert res is Nothing

    def append_1_no_return(alist):
        alist.append(1)

    res = Some([1, 2, 3]).map(append_1_no_return)
    assert res.value is None

    def append_1_return(alist):
        alist.append(1)
        return alist

    res = Some([1, 2, 3]).map(append_1_return)
    assert res.value == [1, 2, 3, 1]

    alist = [1, 2, 3]
    res = Some(alist).map(append_1_return)
    assert res.value is alist

    res = Nothing.map(multiply_2)
    assert res is Nothing


def test_bind():
    def get_foo_option(adict):
        key = 'foo'
        if key in adict:
            return Some(adict[key])
        return Nothing
    foo_adict = {'foo': 'value of foo', 'bar': 'value of bar'}
    nofoo_adict = {'no_foo': 'value of foo', 'bar': 'value of bar'}

    res = Some(foo_adict).bind(get_foo_option)
    assert res.value == 'value of foo'

    res = Nothing.bind(get_foo_option)
    assert res is Nothing

    res = Some(nofoo_adict).bind(get_foo_option)
    assert res is Nothing


def test_comparator():
    some_hello = Some("hello")
    some_hello_2 = Some("hello")
    some_world = Some("world")

    assert some_hello == some_hello_2
    with pytest.raises(TypeError):
        assert some_hello == "hello"

    assert some_hello != some_world
    with pytest.raises(TypeError):
        assert some_hello != "world"

    some_100 = Some(100)
    some_100_2 = Some(100)
    some_200 = Some(200)
    assert some_100 < some_200
    assert some_200 > some_100
    assert some_100.value < 200
    assert some_200.value > 100
    assert some_100 <= some_200
    assert some_200 >= some_100
    assert some_100 <= some_100_2
    assert some_100 >= some_100_2
    with pytest.raises(TypeError):
        assert some_200 < 100
    with pytest.raises(TypeError):
        assert some_200 > 100


def test_get_attr():
    class Person:
        def __init__(self, name, father=None, mother=None):
            self.name = name
            self.father = father
            self.mother = mother

        def get_father(self):
            return self.father

        def get_mother(self):
            return self.mother

        def __repr__(self):
            return f'Person({self.name!r}, {self.father!r}, {self.mother!r})'

    papa = Person('Papa')
    mama = Person('Mama')
    johnny = Person('Johnny', papa, mama)

    # assert maybe_obj.get_data().v == 30
    # assert maybe_obj.get_none().v is None
    # assert maybe_obj.get_none() == Some(None)
    # assert maybe_obj.get_none() is not Nothing
    # assert maybe_obj.fmap_one.get_none().v is None
    # assert maybe_obj.n.get_none() is Nothing
    # assert maybe_obj.get_none.n() is Nothing
    # assert maybe_obj.join()
