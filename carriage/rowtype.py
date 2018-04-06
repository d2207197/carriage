

import attr


@attr.s(slots=True)
class Tuple:

    def __getitem__(self, item_key):
        return attr.astuple(self)[item_key]

    def __iter__(self):
        return iter(attr.astuple(self))

    def evolve(self, **kwargs):
        return attr.evolve(self, **kwargs)

    def transform(self, **kwargs):
        return attr.evolve(
            self,
            {k: f(getattr(self, k))for k, f in kwargs.items()})

    def asdict(self):
        return attr.asdict(self)


# @attr.s(slots=True)
# class CurrPrev(Tuple):
#     curr = attr.ib()
#     prev = attr.ib()


# @attr.s(slots=True)
# class CurrNext(Tuple):
#     curr = attr.ib()
#     next = attr.ib()


# @attr.s(slots=True)
# class ValueIndex(Tuple):
#     value = attr.ib()
#     index = attr.ib()


# @attr.s(slots=True)
# class KeyValues(Tuple):
#     key = attr.ib()
#     values = attr.ib()


class Row(tuple):
    def __new__(self, **kwargs):
        row = tuple.__new__(self, kwargs.values())
        row._dict = kwargs
        return row

    def __hash__(self):
        return hash(self._items)

    def __eq__(self, other):
        return self._items == other._items

    def __ne__(self, other):
        return self._items != other._items

    def __gt__(self, other):
        return self._items > other._items

    def __lt__(self, other):
        return self._items < other._items

    def __ge__(self, other):
        return self._items >= other._items

    def __le__(self, other):
        return self._items <= other._items

    def __iter__(self):
        yield from self._key_to_value.values()

    # def __getitem__(self, item):
    #     if isinstance(item, (int, slice)):
    #         return tuple.__getitem__(self, item)
    #     else:
    #         return self._dict[item]

    def __getattr__(self, name):
        if name in self._dict:
            return self._dict[name]
        else:
            raise AttributeError(f'{self!r} has no attribute {name!r}')

    def evolve(self, **kwargs):
        d = self._dict.copy()
        d.update(kwargs)
        return Row(**d)

    def transform(self, **kwargs):
        d = self._dict.copy()
        d.update({k: f(getattr(self, k))for k, f in kwargs.items()})
        return Row(**d)

    def asdict(self):
        return self._dict.copy()

    def __repr__(self):
        kwargs_str = ', '.join(f'{k}={v!r}' for k, v in self._dict.items())
        return f'Row({kwargs_str})'
