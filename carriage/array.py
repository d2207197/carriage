
import builtins
import collections
import itertools as itt
from copy import copy

from .monad import Monad
from .optional import Nothing, Some
from .rowtype import CurrNext, CurrPrev, ValueIndex


class Array(Monad):
    __slots__ = '_items'

    @classmethod
    def range(cls, start, end=None, step=1):
        if end is None:
            start, end = 0, start

        return cls(range(start, end, step))

    @property
    def _base_type(self):
        return Array

    def __init__(self, items=None):

        if isinstance(items, list):
            pass
        elif isinstance(items, collections.Iterable):
            items = list(items)
        elif items is None:
            items = []
        else:
            raise TypeError("items should be iterable")

        self._items = items

    @classmethod
    def unit(cls, value):
        return Array([value])

    def flat_map(self, to_iterable_action):
        return Array(
            itt.chain.from_iterable(
                to_iterable_action(item)
                for item in self._items))

    def map(self, action):
        return Array(action(item) for item in self._items)

    def flatten(self):
        return Array(itt.chain.from_iterable(self._items))

    def then(self, alist):
        # TODO
        if len(self._items) > 0:
            return alist
        else:
            return self

    def ap(self, avalue):
        # TODO
        pass

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __repr__(self):
        return f'{type(self).__name__}({self._items!r})'

    @property
    def _value_for_cmp(self):
        return self._items

    def len(self):
        return len(self)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Array(self._items[index])
        return self._items[index]

    def get(self, index, default=None):
        if index < len(self):
            return self._items[index]
        return default

    def get_opt(self, index):
        if (index if index >= 0 else abs(index) - 1) < len(self):
            return Some(self._items[index])

        return Nothing

    def first(self):
        return self._items[0]

    def second(self):
        return self._items[1]

    def last(self):
        return self._items[-1]

    def first_opt(self):
        return self.get_opt(0)

    def second_opt(self):
        return self.get_opt(1)

    def last_opt(self):
        return self.get_opt(-1)

    def find(self, pred):
        for item in self._items:
            if pred(item):
                return item

    def find_opt(self, pred):
        for item in self._items:
            if pred(item):
                return Some(item)

        else:
            return Nothing

    def take(self, n):
        return Array(self._items[:n])

    def drop(self, n):
        return Array(self._items[n:])

    def tail(self):
        return Array(self._items[1:])

    def butlast(self):
        return self[:-1]

    def takeright(self, n):
        return Array(self._items[-n:])

    def dropright(self, n):
        return Array(self._items[:-n])

    def slice(self, start, stop, step=None):
        return self[slice(start, stop, step)]

    def takewhile(self, pred):
        return Array(itt.takewhile(pred, self._items))

    def dropwhile(self, pred):
        return Array(itt.dropwhile(pred, self._items))

    def split_before(self, pred):
        def _split_before(pred, items):
            segment = []
            for item in items:
                if pred(item) and len(segment) > 0:
                    yield segment
                    segment = []
                segment.append(item)

            yield segment

        return Array(_split_before(pred, self._items))

    def split_after(self, pred):
        def _split_after(pred, items):
            segment = []
            for item in items:
                if pred(item):
                    yield segment
                    segment = []
                segment.append(item)

            if len(segment) > 0:
                yield segment

        return Array(_split_after(pred, self._items))

    def pluck(self, key):
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        return self.map(lambda d: Some(d[key])
                        if key in d else Nothing)

    def pluck_attr(self, attr):
        return self.map(lambda obj: getattr(obj, attr))

    def filter(self, pred):
        return Array(builtins.filter(pred, self._items))

    def filterfalse(self, pred):
        return Array(itt.filterfalse(pred, self._items))

    def where(self, **conds):
        return self.filter(lambda d:
                           all(key in d and d[key] == value
                               for key, value in conds.items()))

    def without(self, *items):
        items = set(items)
        return self.filter(lambda item: item not in items)

    def interpose(self, sep):
        for item in self._items:
            yield item
            yield

    def zip(self, *iterable):
        return Array(zip(self._items, *iterable))

    def zip_longest(self, *iterables, fillvalue=None):
        return Array(itt.zip_longest(
            self._items, *iterables,
            fillvalue=fillvalue))

    def zip_longest_opt(self, *iterables):
        iterables = [map(Some, it) for it in iterables]
        return Array(itt.zip_longest(map(Some, self._items),
                                     *iterables,
                                     fillvalue=Nothing))

    def zip_prev(self, fillvalue=None):
        prevs = itt.chain([fillvalue], self._items)
        return Array(itt.starmap(CurrPrev, zip(self._items, prevs)))

    def zip_next(self, fillvalue=None):
        items_itr = iter(self._items)
        next(items_itr)
        nexts = itt.chain(items_itr, [fillvalue])
        return Array(itt.starmap(CurrNext, zip(self._items, nexts)))

    def zip_index(self, start=0):
        return Array(itt.starmap(ValueIndex,
                                 zip(self._items, itt.count(start))))

    def starmap(self, action):
        return Array(itt.starmap(action, self._items))

    def reverse(self):
        self._items.reverse()
        return self

    def reversed(self):
        return Array(reversed(self._items))

    def sort(self, key=None, reverse=False):
        self._items.sort(key=key, reverse=reverse)
        return self

    def sorted(self, key=None, reverse=False):
        return Array(sorted(self._items, key=key, reverse=reverse))

    def sum(self):
        return sum(self)

    def accumulate(self, func=None):
        return Array(itt.accumulate(self._items, func))

    def extend(self, iterable):
        self._items.extend(iterable)
        return self

    def extended(self, iterable):
        alist = self.copy()
        alist.extend(iterable)
        return alist

    def append(self, item):
        self._items.append(item)
        return self

    def appended(self, item):
        alist = self.copy()
        alist.append(item)
        return alist

    def distincted(self):
        def _distincted(items):
            item_set = set()
            for item in items:
                if item not in item_set:
                    item_set.add(item)
                    yield item

        return Array(_distincted(self._items))

    def product(self, *iterables, repeat=1):
        return Array(itt.product(self._items, *iterables, repeat=repeat))

    def permutations(self, r=None):
        return Array(itt.permutations(self._items, r=r))

    def combinations(self, r):
        return Array(itt.combinations(self._items, r=r))

    def combinations_with_replacement(self, r):
        return Array(itt.combinations_with_replacement(self._items, r=r))

    def copy(self):
        return Array(copy(self._items))

    def to_list(self, copy=False):
        if copy:
            return self._items
        else:
            return self._items[:]

    def to_series(self):
        # TODO
        pass

    def to_set(self):
        return set(self._items)

    def to_dict(self):
        return {k: v for k, v in self}

    def to_stream(self):
        from .stream import Stream
        return Stream(self)
