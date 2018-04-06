
import builtins
import functools as fnt
import itertools as itt
from collections import Counter, defaultdict, deque

from .array import Array
from .monad import Monad
from .optional import Nothing, Some
from .rowtype import CurrNext, CurrPrev, KeyValues, ValueIndex


def as_stream(f):
    @fnt.wraps(f)
    def wraped(self, *args, **kwargs):
        trfmr = f(self, *args, **kwargs)
        return Stream(self, trfmr)

    return wraped


class Stream(Monad):
    __slots__ = '_iterable', '_transformer'

    def __init__(self, iterable, transformer=None):
        self._iterable = iterable
        self._transformer = transformer

    @classmethod
    def range(cls, start, end=None, step=1):
        if end is None:
            start, end = 0, start

        return cls(range(start, end, step))

    @classmethod
    def count(cls, start, step=1):
        return cls(itt.count(start, step))

    @classmethod
    def repeat(cls, elem, times=None):
        return cls(itt.repeat(elem, times=times))

    @classmethod
    def cycle(cls, iterable):
        return cls(itt.cycle(iterable))

    @classmethod
    def repeatedly(cls, func, times=None):
        def repeatedly_gen(times):
            while True:
                if times is None:
                    yield func()
                elif times > 0:
                    yield func()
                    times -= 1
        return cls(repeatedly_gen())

    @classmethod
    def iterate(cls, func, x):
        def iterate_gen(x):
            while True:
                yield x
                x = func(x)
        return cls(iterate_gen(x))

    @property
    def _base_type(self):
        return Stream

    @classmethod
    def unit(cls, value):
        return Stream([value])

    def to_list(self):
        return list(self)

    @as_stream
    def flat_map(self, to_iterable_action):
        def flat_map_tr(iterable):
            return itt.chain.from_iterable(map(to_iterable_action, iterable))
        return flat_map_tr

    @as_stream
    def map(self, action):
        return fnt.partial(map, action)

    @as_stream
    def flatten(self):
        return itt.chain.from_iterable

    def then(self, alist):
        # TODO
        if len(self._items) > 0:
            return alist
        else:
            return self

    def ap(self, avalue):
        # TODO
        pass

    # def __len__(self):

    def __iter__(self):
        if self._transformer is None:
            return iter(self._iterable)

        return iter(self._transformer(self._iterable))

    def __repr__(self):
        return (f'{type(self).__name__}'
                f'({self._iterable!r}, {self._transformer!r})')

    @property
    def _value_for_cmp(self):
        return list(self)

    def len(self):
        return sum(1 for item in self)

    @classmethod
    def _check_index_range(cls, index):
        if index is not None and index < 0:
            raise ValueError(
                'Stream index should be greater than 0. '
                'Be aware of that indexing an iterator would '
                'consume items from it.')

    def __getitem__(self, index):
        # TODO: support negative index
        if isinstance(index, slice):
            return self.slice(index.start, index.stop, index.step)

        try:
            return next(itt.islice(self, index, None))
        except StopIteration:
            raise IndexError(
                'Stream index out of range. '
                'Be aware of that indexing an iterator would '
                'consume items from it.')

    def get(self, index, default=None):
        # TODO: support negative index
        # dd = deque(aa, maxlen=1)

        self._check_index_range(index)
        return next(itt.islice(self, index, None), default)

    def get_opt(self, index):
        try:
            return Some(self[index])
        except IndexError:
            return Nothing

    @as_stream
    def slice(self, start, stop, step=None):
        self._check_index_range(start)
        self._check_index_range(stop)
        return lambda iterable: itt.islice(iterable, start, stop, step)

    def first(self):
        return self[0]

    def second(self):
        return self[1]

    def last(self):
        return deque(self, 1)[-1]

    def first_opt(self):
        return self.get_opt(0)

    def second_opt(self):
        return self.get_opt(1)

    def last_opt(self):
        dq = deque(self, 1)
        if len(dq) > 0:
            return Some(dq[-1])

        return Nothing

    def find(self, pred):
        for item in self:
            if pred(item):
                return item

    def find_opt(self, pred):
        for item in self:
            if pred(item):
                return Some(item)

        else:
            return Nothing

    def take(self, n):
        return self[:n]

    def drop(self, n):
        return self[n:]

    def tail(self):
        return self[1:]

    # def butlast(self):
    #     # TODO
    #     return self[:-1]

    # def takeright(self, n):
    #     # TODO
    #     return Array(self._items[-n:])

    # def dropright(self, n):
    #     # TODO
    #     return Array(self._items[:-n])

    @as_stream
    def takewhile(self, pred):
        return fnt.partial(itt.takewhile, pred)
    take_while = takewhile

    @as_stream
    def dropwhile(self, pred):
        return fnt.partial(itt.dropwhile, pred)

    drop_while = dropwhile

    @as_stream
    def split_before(self, pred):
        def split_before_tr(iterable):
            segment = []
            for item in iterable:
                if pred(item) and len(segment) > 0:
                    yield Array(segment)
                    segment = []
                segment.append(item)

            yield Array(segment)

        return split_before_tr

    @as_stream
    def split_after(self, pred):
        def split_after_tr(iterable):
            segment = []
            for item in iterable:
                segment.append(item)
                if pred(item):
                    yield Array(segment)
                    segment = []

            if len(segment) > 0:
                yield Array(segment)

        return split_after_tr

    def pluck(self, key):
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        return self.map(lambda d: Some(d[key])
                        if key in d else Nothing)

    def pluck_attr(self, attr):
        return self.map(lambda obj: getattr(obj, attr))

    @as_stream
    def filter(self, pred):
        return fnt.partial(filter, pred)

    @as_stream
    def filterfalse(self, pred):
        return fnt.partial(itt.filterfalse, pred)

    filter_false = filterfalse

    def without(self, *items):
        try:
            items = set(items)
        except TypeError:
            # TODO: warn bad performance
            pass
        return self.filter(lambda item: item not in items)

    def where(self, **conds):
        return self.filter(lambda d:
                           all(key in d and d[key] == value
                               for key, value in conds.items()))

    @as_stream
    def interpose(self, sep):
        def interpose_tr(iterable):
            iterator = iter(iterable)
            yield next(iterator)
            for item in iterator:
                yield sep
                yield item

        return interpose_tr

    @as_stream
    def zip(self, *iterables):
        def zip_tr(items):
            return builtins.zip(items, *iterables)

        return zip_tr

    @as_stream
    def zip_longest(self, *iterables, fillvalue=None):
        def zip_longest_tr(items):
            return itt.zip_longest(items, *iterables, fillvalue=fillvalue)
        return zip_longest_tr

    @as_stream
    def zip_prev(self, fillvalue=None):
        def zip_prev_tr(items):
            items, prevs = itt.tee(items)
            prevs = itt.chain([fillvalue], prevs)
            return itt.starmap(CurrPrev, builtins.zip(items, prevs))
        return zip_prev_tr

    @as_stream
    def zip_next(self, fillvalue=None):
        def zip_next_tr(items):
            items, nexts = itt.tee(items)
            next(nexts, None)
            return itt.starmap(
                CurrNext, itt.zip_longest(items, nexts, fillvalue=fillvalue))
        return zip_next_tr

    def zip_index(self, start=0):
        return self.zip(itt.count(start)).starmap(ValueIndex)

    @as_stream
    def starmap(self, action):
        return fnt.partial(itt.starmap, action)

    @as_stream
    def reversed(self):
        def reversed_tr(items):
            try:
                return reversed(items)
            except TypeError:
                return reversed(list(items))

        return reversed_tr

    @as_stream
    def sorted(self, key=None, reverse=False):
        return fnt.partial(sorted, key=key, reverse=reverse)

    def sum(self):
        return sum(self)

    def reduce(self, func):
        return fnt.reduce(func, self)

    def fold_left(self, func, zero_value):
        return fnt.reduce(func, self, zero_value)

    # def key_by(self, func):
    #     return self.map(lambda elem: Row(key=func(elem), value=elem))

    @as_stream
    def group_by(self, key=None):
        def group_by_tr(self_):
            for k, vs in itt.groupby(self_, key=key):
                yield KeyValues(key=k, values=Stream(vs))
        return group_by_tr

    groupby = group_by

    def dict_group_by(self, key=None):
        key_to_grp = defaultdict(list)
        for elem in self:
            key_to_grp[key(elem)].append(elem)
        return dict(key_to_grp)

    def dict_multi_group_by(self, key=None):
        key_to_grp = defaultdict(list)
        for elem in self:
            for k in key(elem):
                key_to_grp[k].append(elem)
        return dict(key_to_grp)

    @as_stream
    def sliding_window(self, n=2):
        def sliding_window_tr(self_):
            self_itr = iter(self)
            dq = deque(itt.islice(self_itr, n - 1), maxlen=n)
            for item in self_itr:
                dq.append(item)
                yield tuple(dq)
        return sliding_window_tr

    def mean(self):
        length, summation = deque(enumerate(itt.accumulate(self), 1), 1).pop()
        return summation / length

    @as_stream
    def accumulate(self, func=None):
        return fnt.partial(itt.accumulate, func=func)

    def value_counts(self):
        return Counter(self)

    @as_stream
    def extended(self, iterable):
        def extended_tr(self_):
            return itt.chain(self_, iterable)
        return extended_tr

    def appended(self, item):
        return self.extended((item,))

    @as_stream
    def distincted(self):
        def distincted_tr(items):
            item_set = set()
            for item in items:
                if item not in item_set:
                    item_set.add(item)
                    yield item

        return distincted_tr

    @as_stream
    def product(self, *iterables, repeat=1):
        def product_tr(self_):
            return itt.product(self_, *iterables, repeat=repeat)
        return product_tr

    def permutations(self, r=None):
        return fnt.partial(itt.permutations, r=r)

    def combinations(self, r):
        return fnt.partial(itt.combinations, r=r)

    def combinations_with_replacement(self, r):
        return fnt.partial(itt.combinations_with_replacement, r=r)

    # def copy(self):
    #     return Array(copy(self._items))

    def to_series(self):
        import pandas as pd

        return pd.Series(list(self))

    def to_set(self):
        return set(self)

    def to_dict(self):
        return {k: v for k, v in self}

    def to_array(self):
        return Array(self)


# @attr.s(slots=True)
# class CurrNext:
#     curr = attr.ib()
#     next = attr.ib()

#     def __iter__(self):
#         return iter(attr.astuple(self))


# @attr.s(slots=True)
# class ValueIndex:
#     value = attr.ib()
#     index = attr.ib()

#     def __iter__(self):
#         return iter(attr.astuple(self))
