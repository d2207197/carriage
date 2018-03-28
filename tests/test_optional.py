import pytest

from carriage import Nothing, NothingError, Optional, Some


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
    assert Optional.ecall(raise_exception) is Nothing

    def raise_typeerror():
        raise TypeError
    assert Optional.call_exceptable(raise_typeerror, TypeError) is Nothing
    assert Optional.ecall(raise_typeerror, TypeError) is Nothing

    with pytest.raises(TypeError):
        Optional.call_exceptable(raise_typeerror, errors=ValueError)

    def identity(x):
        return x

    assert Optional.ecall(identity, 10).value == 10

    def raise_error(error):
        raise error

    with pytest.raises(TypeError):
        Optional.call_exceptable(raise_error, TypeError, errors=ValueError)

    assert Optional.call_exceptable(raise_error, AttributeError,
                                    errors=AttributeError) is Nothing


def test_noneable():
    @Optional.noneable
    def odd_return_none(n):
        if n % 2 == 1:
            return None
        return n

    assert odd_return_none(3) is Nothing
    assert odd_return_none(4).value == 4


def test_exceptable():
    @Optional.exceptable
    def odd_raise_valueerror(n):
        if n % 2 == 1:
            raise ValueError
        return n

    assert odd_raise_valueerror(3) is Nothing
    assert odd_raise_valueerror(4).value == 4

    @Optional.exceptable(ValueError)
    def odd_raise_valueerror(n):
        if n % 2 == 1:
            raise ValueError
        return n

    assert odd_raise_valueerror(3) is Nothing
    assert odd_raise_valueerror(4).value == 4

    @Optional.exceptable(AttributeError)
    def odd_raise_valueerror(n):
        if n % 2 == 1:
            raise ValueError
        return n

    with pytest.raises(ValueError):
        odd_raise_valueerror(3)
    assert odd_raise_valueerror(4).value == 4

    @Optional.exceptable(AttributeError, ValueError)
    def odd_raise_valueerror(n):
        if n % 2 == 1:
            raise ValueError
        return n

    assert odd_raise_valueerror(3) is Nothing
    assert odd_raise_valueerror(4).value == 4


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

    res = Some(100).fmap(multiply_2)
    assert res.value == 200

    res = Nothing.map(multiply_2)
    assert res is Nothing

    res = Nothing.fmap(multiply_2)
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


def test_flat_map():
    def get_foo_option(adict):
        key = 'foo'
        if key in adict:
            return Some(adict[key])
        return Nothing

    foo_adict = {'foo': 'value of foo', 'bar': 'value of bar'}
    nofoo_adict = {'no_foo': 'value of foo', 'bar': 'value of bar'}

    res = Some(foo_adict).flat_map(get_foo_option)
    assert res.value == 'value of foo'

    res = Nothing.flat_map(get_foo_option)
    assert res is Nothing

    res = Some(nofoo_adict).flat_map(get_foo_option)
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: d.get('foo'))
           .flat_map(Optional.value_noneable))
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: Optional.value_noneable(d.get('foo')))
           .join())
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: Optional.value_noneable(d.get('foo')))
           .flatten())
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: d.get('foo'))
           .join_noneable())
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: d.get('bar'))
           .join_noneable())
    assert res.value == 'value of bar'


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


def test_value_do():
    class Person:
        def __init__(self, name, age, father=None, mother=None):
            self.name = name
            self.age = age
            self.father = father
            self.mother = mother

        def get_father(self):
            return self.father

        def get_mother(self):
            return self.mother

        def __repr__(self):
            return f'Person({self.name!r}, {self.father!r}, {self.mother!r})'

        def __eq__(self, other):
            return (self.name, self.father, self.mother) == (other.name, other.father, other.mother)

    papa = Person('Papa', 45)
    mama = Person('Mama', 40)
    johnny = Person('Johnny', 18, papa, mama)

    assert Some(johnny).value_do.mother == Some(mama)
    assert Some(johnny).value_do.mother.value is mama
    assert Some(johnny).value_do.age == Some(18)
    assert Some(johnny).value_do.age < Some(johnny).value_do.mother.value_do.age

    # assert maybe_obj.get_data().v == 30
    # assert maybe_obj.get_none().v is None
    # assert maybe_obj.get_none() == Some(None)
    # assert maybe_obj.get_none() is not Nothing
    # assert maybe_obj.fmap_one.get_none().v is None
    # assert maybe_obj.n.get_none() is Nothing
    # assert maybe_obj.get_none.n() is Nothing
    # assert maybe_obj.join()
