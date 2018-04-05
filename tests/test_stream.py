import itertools as itt
import operator as op
from collections import Counter, defaultdict

import pandas as pd
import pytest
from carriage import Array, Nothing, Some, Stream
from carriage.types import CurrNext, CurrPrev, ValueIndex


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
        return (self.name, self.father, self.mother) == (
            other.name, other.father, other.mother)


def test_init():
    assert Stream([1, 2, 3]).to_list() == [1, 2, 3]
    assert Stream(range(10)).to_list() == list(range(10))
    assert Stream.range(10).to_list() == list(range(10))


def test_access():
    assert Stream.range(5, 10).get(3) == 8
    assert Stream.range(5, 10).get(5, 0) == 0
    assert Stream.range(5, 10).get(7, 0) == 0
    assert Stream.range(5, 10).get(6) is None
    with pytest.raises(ValueError):
        assert Stream.range(5, 10).get(-1) is None
    assert Stream.range(5, 10)[3] == 8
    with pytest.raises(ValueError):
        assert Stream.range(5, 10)[-1]
    with pytest.raises(IndexError):
        assert Stream.range(5, 10)[5]

    assert Stream.range(5, 10).get_opt(3) == Some(8)
    assert Stream.range(5, 10).get_opt(5) is Nothing
    with pytest.raises(ValueError):
        assert Stream.range(5, 10).get_opt(-1) is Nothing

    assert Stream.range(5, 10).first() == 5
    assert Stream.range(5, 10).first_opt() == Some(5)
    assert Stream([5]).first_opt() == Some(5)
    assert Stream([]).first_opt() is Nothing
    assert Stream(iter([])).first_opt() is Nothing


def test_slice():
    assert Stream.range(5, 10).take(3).to_list() == [5, 6, 7]
    assert Stream.range(5, 10).drop(3).to_list() == [8, 9]

    def less_than_3(n):
        return n < 3

    assert Stream.range(0, 5).takewhile(less_than_3).to_list() == [0, 1, 2]

    assert Stream.range(0, 5).dropwhile(less_than_3).to_list() == [3, 4]


def test_split():
    def divisible_by_three(n):
        return n % 3 == 0
    assert Stream.range(10).split_before(divisible_by_three).to_list() == [
        Array([0, 1, 2]), Array([3, 4, 5]), Array([6, 7, 8]), Array([9])]
    assert Stream.range(10).split_after(divisible_by_three).to_list() == [
        Array([0]), Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]


def test_pluck():
    assert Stream([{'a': 1, 'b': 2}, {'a': 4, 'b': 5}]
                  ).pluck('a').to_list() == [1, 4]
    assert Stream([{'a': 1, 'b': 2}, {'b': 3}, {'a': 4, 'b': 5}]).pluck_opt(
        'a').to_list() == [Some(1), Nothing, Some(4)]

    people = [Person('Johnny', 18), Person('Amy', 15)]
    assert Stream(people).pluck_attr('name').to_list() == ['Johnny', 'Amy']


def test_filtering():
    def is_even(n):
        return n % 2 == 0
    assert Stream.range(5, 10).filter(is_even).to_list() == [6, 8]
    assert Stream.range(5, 10).filterfalse(is_even).to_list() == [5, 7, 9]

    assert Stream.range(5, 10).without(6, 8).to_list() == [5, 7, 9]
    assert (Stream([{'a': 1, 'b': 2}, {'a': 4, 'b': 5}, {'a': 1, 'b': 3}])
            .where(a=1).to_list() ==
            [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}])


def test_interpose():
    assert Stream.range(5, 9).interpose(0).to_list() == [5, 0, 6, 0, 7, 0, 8]
    assert Stream([]).interpose(0).to_list() == []


def test_map():

    def multiply_2(n):
        return n * 2

    assert Stream.range(10).map(multiply_2).to_list() == list(range(0, 20, 2))

    def duplicate(v):
        return [v] * 2

    assert Stream.range(3).flat_map(duplicate).to_list() == [0, 0, 1, 1, 2, 2]

    assert Stream([(5, 1), (3, 4)]).flatten().to_list() == [5, 1, 3, 4]
    assert Stream.range(10).len() == 10
    assert Stream([(5, 1), (3, 4)]).flatten().len() == 4


def test_zip():
    assert Stream.range(5, 8).zip(itt.count(1)).to_list() == [
        (5, 1), (6, 2), (7, 3)]
    assert Stream.range(5, 8).zip(itt.count(1)).to_list() == [
        (5, 1), (6, 2), (7, 3)]

    assert Stream.range(5, 8).zip_longest(range(1, 5)).to_list() == [
        (5, 1), (6, 2), (7, 3), (None, 4)
    ]

    assert Stream.range(5, 8).zip_longest(range(1, 5), fillvalue=100).to_list() == [
        (5, 1), (6, 2), (7, 3), (100, 4)
    ]

    assert Stream.range(5, 8).zip_prev().to_list() == [
        CurrPrev(5, None), CurrPrev(6, 5), CurrPrev(7, 6)
    ]

    assert Stream.range(5, 8).zip_next().to_list() == [
        CurrNext(5, 6), CurrNext(6, 7), CurrNext(7, None)
    ]

    assert Stream.range(5, 8).zip_prev(99).to_list() == [
        CurrPrev(5, 99), CurrPrev(6, 5), CurrPrev(7, 6)
    ]

    assert Stream.range(5, 8).zip_next(99).to_list() == [
        CurrNext(5, 6), CurrNext(6, 7), CurrNext(7, 99)
    ]

    assert Stream.range(5, 8).zip_index().to_list() == [
        ValueIndex(5, 0), ValueIndex(6, 1), ValueIndex(7, 2)
    ]


def test_ordering():
    assert Stream.range(5, 8).reversed().to_list() == [7, 6, 5]
    assert Stream([1, 3, 2, 4]).sorted().to_list() == [1, 2, 3, 4]
    assert Stream([1, 3, 2, 4]).sorted(lambda x: -x).to_list() == [4, 3, 2, 1]
    assert Stream([1, 3, 2, 4]).sorted(lambda x:
                                       x % 2).to_list() == [2, 4, 1, 3]


def test_reduce():
    assert Stream.range(5, 8).reduce(lambda a, b: a + b) == 18
    assert Stream.range(5, 8).fold_left(lambda a, b: a + b, 2) == 20
    assert Stream.range(5, 8).mean() == 6
    assert Stream.range(5, 8).sum() == 18
    assert Stream.range(5, 8).accumulate().to_list() == [5, 11, 18]
    assert Stream.range(5, 8).accumulate(op.mul).to_list() == [5, 30, 210]


def test_extend():
    assert Stream.range(5, 8).extended([1, 3]).to_list() == [5, 6, 7, 1, 3]
    assert Stream.range(5, 8).appended(5).to_list() == [5, 6, 7, 5]


def test_distincted():
    assert Stream([1, 5, 1, 3, 3, 5, 6]
                  ).distincted().to_list() == [1, 5, 3, 6]


def test_to():
    assert Stream.range(5, 8).to_array() == Array([5, 6, 7])
    assert Stream([(1, 2), (3, 4)]).to_dict() == {1: 2, 3: 4}
    assert Stream.range(5, 8).to_set() == set([5, 6, 7])

    assert list(Stream.range(5, 8)) == [5, 6, 7]
    assert Stream.range(5, 8).to_series().equal(pd.Series([5, 6, 7]))


def test_ngram():
    assert Stream.range(5, 10).ngram(3).to_list() == [
        (5, 6, 7), (6, 7, 8), (7, 8, 9)]


def test_counter():
    assert Stream([3, 1, 1, 3, 5, 4, 9, 3, 1, 5, 3]).value_counts(
    ) == Counter([3, 1, 1, 3, 5, 4, 9, 3, 1, 5, 3])


def test_groupby():
    assert Stream.range(10).groupby(lambda n: n // 3).starmap(lambda k, vs: (k, list(vs))).to_list() == [
        (0, [0, 1, 2]), (1, [3, 4, 5]), (2, [6, 7, 8]), (3, [9])
    ]
    assert Stream.range(10).groupby_as_dict(
        lambda n: n // 3) == {0: [0, 1, 2], 1: [3, 4, 5], 2: [6, 7, 8], 3: [9]}
