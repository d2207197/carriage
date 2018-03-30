
import collections
import itertools as itt
from copy import copy

import attr

from .monad import Monad
from .optional import Nothing_inst as Nothing
from .optional import Optional, Some


@attr.s
class CurPrev:
    cur = attr.ib()
    prev = attr.ib()


@attr.s
class CurNext:
    cur = attr.ib()
    next = attr.ib()


@attr.s
class CurIndex:
    cur = attr.ib()
    index = attr.ib()


class List(Monad):
    @classmethod
    def range(cls, start, end=None, step=1):
        if end is None:
            start, end = 0, start

        return cls(range(start, end, step))

    @property
    def _base_type(self):
        return List

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
        return List([value])

    def flat_map(self, to_iterable_action):
        return List(
            itt.chain.from_iterable(
                to_iterable_action(item)
                for item in self._items))

    def map(self, action):
        return List(action(item) for item in self._items)

    def flatten(self):
        return List(itt.chain.from_iterable(self._items))

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

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return List(self._items[idx])
        return self._items[idx]

    def get(self, idx, default=None):
        if idx < len(self):
            return self._items[idx]
        return default

    def get_opt(self, idx):
        if (idx if idx >= 0 else abs(idx) - 1) < len(self):
            return Some(self._items[idx])

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
        return List(self._items[:n])

    def drop(self, n):
        return List(self._items[n:])

    def tail(self):
        return List(self._items[1:])

    def butlast(self):
        return self[:-1]

    def takeright(self, n):
        return List(self._items[-n:])

    def dropright(self, n):
        return List(self._items[:-n])

    def slice(self, start, stop, step=None):
        return self[slice(start, stop, step)]

    def takewhile(self, pred):
        def _takewhile(items):
            for item in items:
                if not pred(item):
                    break
                yield item

        return List(_takewhile(self._items))

    def dropwhile(self, pred):
        for idx, item in enumerate(self._items):
            if not pred(item):
                return List(self._items[idx:])

    def split_when(self, pred):
        def _split_when(pred, items):
            segment = []
            for item in items:
                if pred(item) and len(segment) > 0:
                    yield segment
                    segment = []
                segment.append(item)

        return List(_split_when(pred, self._items))

    def pluck(self, key):
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        return self.map(lambda d: Some(d[key])
                        if key in d else Nothing)

    def pluck_attr(self, attr):
        return self.map(lambda obj: getattr(obj, attr))

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
        return List(zip(self._items, iterable))

    def zip_longest(self, *iterables, fillvalue=None):
        return List(itt.zip_longest(self._items, *iterables, fillvalue))

    def zip_longest_opt(self, *iterables):
        iterables = [map(Some, it) for it in iterables]
        return List(itt.zip_longest(map(Some, self._items),
                                    *iterables,
                                    Nothing))

    def zip_prev(self, fillvalue=None):
        prevs = itt.chain([fillvalue], self._items)
        return List(map(CurPrev, zip(self._items, prevs)))

    def zip_next(self, fillvalue=None):
        items_itr = iter(self._items)
        next(items_itr)
        nexts = itt.chain(items_itr, [fillvalue])
        return List(map(CurNext, zip(self._items, nexts)))

    def zip_index(self, start=0):
        return List(map(CurIndex, zip(self._items, itt.count(start))))

    def starmap(self, action):
        return List(itt.starmap(action, self._items))

    def product(self, repeat=1):
        return List(itt.product(self._items, repeat=repeat))

    def permutations(self, r):
        return List(itt.permutations(self._items, r=r))

    def combinations(self, r):
        return List(itt.combinations(self._items, r=r))

    def combinations_with_replacement(self, r):
        return List(itt.combinations_with_replacement(self._items, r=r))

    def filter(self, pred):
        return List(filter(pred, self._items))

    def copy(self):
        return List(copy(self._items))

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

    def reversed(self):
        return List(reversed(self._items))

    def distincted(self):

        def _distincted(items):
            item_set = set()
            for item in items:
                if item not in item_set:
                    item_set.add(item)
                    yield item

        return List(_distincted(self._items))

    def sorted(self, key=None, reverse=False):
        return List(sorted(self._items, key=key, reverse=reverse))


class Stream(Monad):
    pass
