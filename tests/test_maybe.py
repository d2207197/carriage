import pytest

from maybee import Just, Nothing, NothingError, maybe_none


def test_maybe_none_init():
    nothing = maybe_none(None)
    assert nothing is Nothing
    with pytest.raises(NothingError):
        Nothing.value

    just = maybe_none(30)
    assert type(just) is Just
    assert just.value == 30

    just = maybe_none("hello")
    assert type(just) is Just
    assert just.value == "hello"

    adict = {'apple': 1, 'orange': 2}
    just = maybe_none(adict)
    assert type(just) is Just
    assert just.value == {'apple': 1, 'orange': 2}
    assert just.value is adict


def test_just_value():
    assert Just(30).value == 30
    assert Just(None).value is None
    assert Just(None).value is None
    assert Just([1, 2, 3]).value == [1, 2, 3]
    alist = [4, 5, 6]
    assert Just(alist).value is alist
    assert Just({'apple': 1, 'orange': 2}).value == {'apple': 1, 'orange': 2}
    adict = {'apple': 1, 'orange': 2}
    assert Just(adict).value is adict


def test_get_or():
    assert Just(30).get_or(None) == 30
    assert Just(None).get_or(None) is None
    assert Just(None).get_or(True) is None
    assert Just([1, 2, 3]).get_or(True) == [1, 2, 3]

    assert Nothing.get_or(0) == 0
    assert Nothing.get_or(None) is None
    assert Nothing.get_or(False) is False
    assert Nothing.get_or(True) is True
    assert Nothing.get_or("A string") == "A string"


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
    # assert maybe_obj.get_none() == Just(None)
    # assert maybe_obj.get_none() is not Nothing
    # assert maybe_obj.fmap_one.get_none().v is None
    # assert maybe_obj.n.get_none() is Nothing
    # assert maybe_obj.get_none.n() is Nothing
    # assert maybe_obj.join()


def test_dict():

    d = {
        '1': {
            '2': {
                '3': 123
            },
            '3': 13,
        },
        '2': 2
    }


def test_eq_ne_comparator():
    just_hello = Just("hello")
    just_hello_2 = Just("hello")
    just_world = Just("world")

    assert just_hello == just_hello_2
    with pytest.raises(TypeError):
        assert just_hello == "hello"

    assert just_hello != just_world
    with pytest.raises(TypeError):
        assert just_hello != "world"


def test_gt_lt_ge_le_comparator():
    just_100 = Just(100)
    just_100_2 = Just(100)
    just_200 = Just(200)
    assert just_100 < just_200
    assert just_200 > just_100
    assert just_100.value < 200
    assert just_200.value > 100
    assert just_100 <= just_200
    assert just_200 >= just_100
    assert just_100 <= just_100_2
    assert just_100 >= just_100_2
    with pytest.raises(TypeError):
        assert just_200 < 100
    with pytest.raises(TypeError):
        assert just_200 > 100


def test_fmap():
    def multiply_2(n):
        return n * 2
    fmap_res = Just(100).fmap(multiply_2)
    fmap_res.value == 200

    fmap_res = Nothing.fmap(multiply_2)
    fmap_res is Nothing


# def test_function():
#     value = 50
#     m = Maybe.except_call(lambda: value)
#     assert isinstance(m, Just)
#     assert m.get() == value
#     assert m.get_or(None) == value
#     assert m.get_or("Yo") == value
