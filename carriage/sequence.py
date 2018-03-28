
import collections
import itertools as itt
from copy import copy

from .monad import Monad
from .optional import Nothing_inst as Nothing
from .optional import Optional, Some


class List(Monad):
    @property
    def _base_type(self):
        return List

    def __init__(self, items):
        if isinstance(items, list):
            pass
        elif isinstance(items, collections.Iterable):
            items = list(items)
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

    def take(self, n):
        return List(self._items[:n])

    def drop(self, n):
        return List(self._items[n:])

    def slice(self, start, stop, step=None):
        return self[slice(start, stop, step)]

    def first(self):
        return self._items[0]

    def last(self):
        return self._items[-1]

    def filter(self, pred):
        return List(filter(pred, self._items))

    def first_optional(self):
        return self.get_optional(0)

    def last_optional(self):
        return self.get_optional(-1)

    def get_optional(self, idx):
        if idx < len(self):
            return Some(self._items[idx])

        return Nothing

    def get(self, idx, default):
        self._items.get(idx, default)

    def copy(self):
        return List(copy(self._items))

    def extend(self, iterable):
        self._items.extend(iterable)
        return self

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

        def distinct(items):
            item_set = set()
            for item in items:
                if item not in item_set:
                    item_set.add(item)
                    yield item

        return List(distinct(self._items))

    def sorted(self, key=None, reverse=False):
        return List(sorted(self._items, key=key, reverse=reverse))

    def take_while(self, pred):
        def take_while(items):
            for item in items:
                if not pred(item):
                    break
                yield item

        return List(take_while(self._items))

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return List(self._item[idx])
        return self._items[idx]


class Stream(Monad):
    pass
