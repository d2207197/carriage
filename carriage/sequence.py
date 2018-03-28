
import collections
import itertools as itt

from .monad import Monad


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
        if len(self._items) > 0:
            return alist
        else:
            return self

    def ap(self, avalue):
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


class Stream(Monad):
    pass
