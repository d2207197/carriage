import itertools as itt
import operator as op
from collections import Counter

import pandas as pd
import pytest
from carriage import Array, Nothing, Some, Stream
from carriage.rowtype import CurrNext, CurrPrev, Row, ValueIndex


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

    assert (Stream.range(5, 8).zip_longest(range(1, 5), fillvalue=100)
            .to_list() == [(5, 1), (6, 2), (7, 3), (100, 4)])

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
    assert Stream.range(5, 8).to_series().equals(pd.Series([5, 6, 7]))


def test_sliding_window():
    assert Stream.range(5, 10).sliding_window(3).to_list() == [
        (5, 6, 7), (6, 7, 8), (7, 8, 9)]


def test_counter():
    assert Stream([3, 1, 1, 3, 5, 4, 9, 3, 1, 5, 3]).value_counts(
    ) == Counter([3, 1, 1, 3, 5, 4, 9, 3, 1, 5, 3])


def test_groupby():
    assert (Stream
            .range(10)
            .groupby(lambda n: n // 3)
            .starmap(lambda k, vs: (k, list(vs))).to_list() ==
            [(0, [0, 1, 2]), (1, [3, 4, 5]), (2, [6, 7, 8]), (3, [9])])

    assert Stream.range(10).map_group_by(
        lambda n: n // 3) == {0: [0, 1, 2], 1: [3, 4, 5], 2: [6, 7, 8], 3: [9]}


@pytest.fixture
def ipsum():
    return '''Lorem ipsum dolor sit amet consectetur adipiscing elit tempus luctus pellentesque senectus donec neque convallis, vivamus laoreet morbi mattis ridiculus etiam aptent at lacus penatibus magna blandit odio. Conubia parturient fringilla lobortis maecenas imperdiet habitasse sociosqu litora, nullam integer sed eget nulla penatibus nec, natoque cubilia tempus ut phasellus mollis gravida. Sagittis ornare dis fames duis faucibus class netus lacinia interdum tellus, pretium quis massa arcu non parturient posuere ullamcorper dapibus volutpat, nisi curabitur augue aenean hac viverra per primis diam. Pulvinar volutpat posuere tempor eleifend diam nascetur erat id proin mollis vulputate, leo aliquam bibendum donec in augue vel integer sagittis nullam platea turpis, potenti iaculis sociis hendrerit tellus penatibus arcu himenaeos litora elementum. Integer posuere montes velit euismod id eget sapien congue ullamcorper eleifend, natoque curae magna ac vel conubia nunc ante tellus, sem dapibus iaculis eu ultricies nec luctus viverra aptent. Taciti nibh tincidunt primis fermentum aenean laoreet nostra, ut sollicitudin porta at viverra venenatis ultrices purus, varius dui velit pulvinar cras interdum. Ante massa a venenatis et quis arcu placerat, curabitur dictumst at vehicula netus nascetur, rhoncus ligula ad est lacus ac.

A conubia taciti quisque dignissim leo volutpat euismod, mus maecenas tempus porta tortor fermentum mollis quis, feugiat rutrum hendrerit convallis etiam congue. Iaculis tincidunt porta litora libero luctus himenaeos, vitae ultrices nulla integer ac auctor cubilia, pharetra inceptos eleifend netus curabitur. Urna congue mauris velit iaculis himenaeos egestas fringilla accumsan placerat, nisi mi erat lacus volutpat porta suscipit donec, imperdiet in ad curabitur hendrerit viverra taciti natoque. Nisi tempus dictumst quis risus eros parturient nostra duis ante et nascetur placerat nunc ullamcorper primis, sapien mollis auctor ultrices laoreet nulla enim consequat in vehicula litora molestie donec. Ad tempus faucibus nam magna enim nullam tincidunt natoque accumsan lacinia, pharetra suspendisse varius porttitor potenti taciti nisl mollis nunc risus, erat vivamus pretium nostra felis dis mauris blandit justo. Ridiculus netus curae est arcu scelerisque sociosqu mus, faucibus fermentum praesent elementum facilisis ut, pellentesque posuere ullamcorper etiam maecenas a.

Sem taciti integer pharetra magnis magna morbi ante cursus per, iaculis justo nunc in a vivamus rhoncus scelerisque, tempus laoreet dictumst ornare primis natoque odio proin. Congue arcu tempor penatibus mi tristique dis egestas, viverra ad integer hac accumsan senectus suscipit pretium, mollis leo erat sodales fermentum turpis. Porta nisl dis facilisi gravida magna, magnis sem massa torquent integer, dui tortor non conubia. Tristique non nullam cursus porta semper tincidunt interdum litora per, vestibulum cum elementum lacinia magna erat posuere nostra, sociis condimentum iaculis praesent hendrerit mi vulputate cubilia. Est nulla ut nec phasellus volutpat convallis velit sed porttitor, elementum eros ullamcorper primis taciti condimentum morbi tortor purus ac, class mattis etiam euismod auctor non quis vehicula. Mus elementum sodales eleifend nam condimentum posuere potenti rhoncus libero pretium, imperdiet sem sociosqu dictumst fermentum leo varius aliquam proin integer sociis, a curabitur iaculis vulputate urna aliquet porta placerat dictum. Ullamcorper vestibulum ante nostra curae cras tempor praesent eros nascetur at integer, lectus porttitor nulla ultrices iaculis torquent dis aliquet dictum hac ridiculus, facilisi justo mi netus varius magnis enim euismod felis himenaeos.
'''


def test_general_case(ipsum, capsys):
    out = (Stream(ipsum.splitlines())
           .flat_map(lambda line: line.split(' '))
           .map(lambda word: word.strip(',.'))
           .filter(lambda word: len(word) > 0)
           .distincted()
           .sorted(key=lambda word: len(word))
           .group_by(lambda word: len(word))
           .map(lambda keyvalues:
                keyvalues.transform(values=lambda stream: stream.to_array()))
           .map(lambda keyvalues: Row(
               length=keyvalues.key, count=keyvalues.values.len()))
           .tap(2, tag='length count')
           .nlargest(3, key=lambda row: row.count)
           .pluck_attr('length')
           .to_list()
           )
    assert out == [6, 7, 8]
    captured = capsys.readouterr()
    assert captured.out == '''length count:0: Row(length=1, count=2)
length count:1: Row(length=2, count=10)
'''
    assert captured.err == ''
