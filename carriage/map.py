import itertools as itt
from collections import UserDict, defaultdict

from .array import Array
from .optional import Nothing, Some
from .rowtype import KeyValue, Row
from .stream import Stream


def identity(_): return _


class Map(UserDict):
    '''A mutable dictionary enhanced with a bulk of useful methods.
    '''

    def update(self, *args, **kwds):
        '''Update Map from dict/iterable and ``return self``

        >>> m = Map(a=3, b=4)
        >>> m2 = m.update(a=5, c=3).update({'d': 2})
        >>> m is m2
        True
        >>> m
        Map({'a': 5, 'b': 4, 'c': 3, 'd': 2})
        '''
        super().update(*args, **kwds)
        return self

    def updated(self, *args, **kwds):
        '''Create a new Map instance that is updated from dict/iterable.
        This method is the same as ``m.copy().update(...)``

        >>> m = Map(a=3, b=4)
        >>> m2 = m.updated(a=5, c=3).update({'d': 2})
        >>> m2
        Map({'a': 5, 'b': 4, 'c': 3, 'd': 2})
        >>> m
        Map({'a': 3, 'b': 4})
        '''
        m = self.copy()
        return m.update(*args, **kwds)

    def join(self, *others, fillvalue=None, agg=None):
        """Create a new Map instance with keys merged and values joined.

        >>> m1 = Map(a=1, b=2)
        >>> m2 = m1.join(dict(a=3, b=4, c=5))
        >>> m2 is m1
        False
        >>> m2
        Map({'a': Row(v0=1, v1=3), 'b': Row(v0=2, v1=4), 'c': Row(v0=None, v1=5)})

        >>> m1 = Map(a=1, b=2)
        >>> m2 = m1.join(dict(a=3, b=4, c=5), agg=sum, fillvalue=0)
        >>> m2
        Map({'a': 4, 'b': 6, 'c': 5})
        """
        return Map(self.iter_joined(*others, fillvalue=fillvalue, agg=agg))

    def iter_joined(self, *others, fillvalue=None, agg=None):
        """Create a ``Row(key, Row(v0, v1, ...))`` iterator with keys from
        all Maps and value joined.

        >>> m = Map(a=1, b=2)
        >>> l = list(m.iter_joined(
        ...          Map(a=3, b=4, c=5),
        ...          Map(a=6, c=7),
        ...          fillvalue=0))
        >>> l[0]
        Row(key='a', values=Row(v0=1, v1=3, v2=6))
        >>> l[1]
        Row(key='b', values=Row(v0=2, v1=4, v2=0))
        >>> l[2]
        Row(key='c', values=Row(v0=0, v1=5, v2=7))
        """
        if agg is None:
            agg = identity

        keys = list(self.keys())
        keys_set = set(keys)
        for other in others:
            for key in other.keys():
                if key not in keys_set:
                    keys_set.add(key)
                    keys.append(key)

        dicts = (self,) + others
        for key in keys:
            yield Row(key=key,
                      values=agg(Row.from_iterable(
                          d.get(key, fillvalue)
                          for d in dicts)))

    def __repr__(self):
        return f'Map({super().__repr__()})'

    def map(self, func):
        '''Create a new Map instance that each key, value pair is derived by
        applying function to original key, value.


        >>> Map(a=3, b=4).map(lambda k, v: (v, k))
        Map({3: 'a', 4: 'b'})

        Parameters
        ----------
        func : ``pred(key, value) -> (key, value)``
            function for computing new key/value pair
        '''
        return Map(func(key, value) for key, value in self.items())

    def map_keys(self, func):
        '''Create a new Map instance that all values remains the same,
        while each corresponding key is updated by applying function to
        original key, value.

        >>> Map(a=3, b=4).map_keys(lambda k, v: k + '_1')
        Map({'a_1': 3, 'b_1': 4})

        Parameters
        ----------
        func : ``pred(key, value) -> key``
            function for computing new keys
        '''
        return Map((func(key, value), value) for key, value in self.items())

    def map_values(self, func):
        '''Create a new Map instance that all keys remains the same,
        while each corresponding value is updated by applying function to
        original key, value.

        >>> Map(a=3, b=4).map_values(lambda k, v: v * 2)
        Map({'a': 6, 'b': 8})

        Parameters
        ----------
        func : ``pred(key, value) -> value``
            function for computing new values
        '''
        return Map((key, func(key, value)) for key, value in self.items())

    def revamp_values(self, func):
        '''Update values of current Map and return self.
        Each value is derived by computing the function using
        both key and value.


        >>> m = Map(a=3, b=4)
        >>> m.revamp_values(lambda k, v: v * 2)
        Map({'a': 6, 'b': 8})
        >>> m
        Map({'a': 6, 'b': 8})

        Parameters
        ----------
        func : ``pred(key, value) -> value``
            function for computing new values

        '''
        for key, value in self.items():
            self[key] = func(key, value)
        return self

    def keep(self, *keys):
        '''Delete keys not specified and return self

        >>> m = Map(a=3, b=4, c=5)
        >>> m.keep('a', 'c')
        Map({'a': 3, 'c': 5})
        >>> m
        Map({'a': 3, 'c': 5})
        '''
        keys = set(keys)
        current_keys = set(self.keys())
        keys_to_delete = current_keys - keys
        for key, in keys_to_delete:
            del self[key]

        return self

    def project(self, *keys):
        '''Create a new Map instance contains only specified keys.

        >>> m = Map(a=3, b=4, c=5)
        >>> m.project('a', 'c')
        Map({'a': 3, 'c': 5})
        >>> m
        Map({'a': 3, 'b': 4, 'c': 5})
        '''
        return Map((k, self[k]) for k in keys)

    def get_opt(self, key):
        '''Get the value of specified key as Optional type.
        Return Some(value) if key exists, otherwise return Nothing.

        >>> m = Map(a=3, b=4)
        >>> m.get_opt('a')
        Some(3)
        >>> m.get_opt('c')
        Nothing
        >>> m.get_opt('a').map(lambda v: v * 2)
        Some(6)
        >>> m.get_opt('c').map(lambda v: v * 2)
        Nothing
        '''

        if key in self:
            return Some(self[key])
        return Nothing

    def remove(self, *keys):
        '''Delete keys and return self

        >>> m = Map(a=3, b=4, c=5)
        >>> m.remove('a', 'c')
        Map({'b': 4})
        >>> m
        Map({'b': 4})
        '''
        for key in keys:
            del self[key]

        return self

    def without(self, *keys):
        '''Create a new Map instance with those keys

        >>> m = Map(a=3, b=4, c=6)
        >>> m.without('a', 'c')
        Map({'b': 4})
        >>> m
        Map({'a': 3, 'b': 4, 'c': 6})
        '''
        return Map((key, value)
                   for key, value in self.items()
                   if key not in keys)

    def retain(self, pred):
        '''Delete key/value pairs not satisfying the predicate and return self

        >>> m = Map(a=3, b=4, c=5)
        >>> m.retain(lambda k, v: k == 'b' or v == 5)
        Map({'b': 4, 'c': 5})
        >>> m
        Map({'b': 4, 'c': 5})

        Parameters
        ----------
        pred : ``(k, v) -> bool``
        '''

        keys_to_delete = []
        for key, value in self.items():
            if not pred(key, value):
                keys_to_delete.append(key)

        return self.remove(*keys_to_delete)

    def retain_false(self, pred):
        '''Delete key/value pairs not satisfying the predicate and return self

        >>> m = Map(a=3, b=4, c=5)
        >>> m.retain_false(lambda k, v: k == 'b' or v == 5)
        Map({'a': 3})
        >>> m
        Map({'a': 3})

        Parameters
        ----------
        pred : ``(k, v) -> bool``
        '''

        keys_to_delete = []
        for key, value in self.items():
            if pred(key, value):
                keys_to_delete.append(key)

        return self.remove(*keys_to_delete)

    def retain_by_key(self, pred):
        '''Delete key/value pairs not satisfying the predicate and return self

        >>> m = Map(a=3, b=4, c=5)
        >>> m.retain_by_key(lambda k: k == 'b')
        Map({'b': 4})
        >>> m
        Map({'b': 4})

        Parameters
        ----------
        pred : ``(k) -> bool``
        '''

        keys_to_delete = []
        for key, value in self.items():
            if not pred(key):
                keys_to_delete.append(key)

        return self.remove(*keys_to_delete)

    def retain_by_value(self, pred):
        '''Delete key/value pairs not satisfying the predicate and return self

        >>> m = Map(a=3, b=4, c=5)
        >>> m.retain_by_value(lambda v: v == 4)
        Map({'b': 4})
        >>> m
        Map({'b': 4})

        Parameters
        ----------
        pred : ``(k) -> bool``
        '''

        keys_to_delete = []
        for key, value in self.items():
            if not pred(value):
                keys_to_delete.append(key)

        return self.remove(*keys_to_delete)

    def filter(self, pred):
        '''Create a new Map with key/value pairs satisfying the predicate

        >>> m = Map({1: 2, 2: 4, 3: 6})
        >>> m2 = m.filter(lambda k, v: (v-k) % 3 == 0)
        >>> m2
        Map({3: 6})

        Parameters
        ----------
        pred : ``(k, v) -> bool``
            predicate

        '''

        return Map((k, v) for k, v in self.items() if pred(k, v))

    def filter_false(self, pred):
        '''Create a new Map with key/value pairs not satisfying the predicate

        >>> m = Map({1: 2, 2: 4, 3: 6})
        >>> m2 = m.filter_false(lambda k, v: (v-k) % 3 == 0)
        >>> m2
        Map({1: 2, 2: 4})

        Parameters
        ----------
        pred : ``(k, v) -> bool``
            predicate
        '''
        return Map((k, v) for k, v in self.items() if not pred(k, v))

    def filter_by_key(self, pred):
        '''Create a new Map with keys satisfying the predicate

        >>> m = Map({1: 2, 2: 4, 3: 6})
        >>> m2 = m.filter_by_key(lambda k: k % 3 == 0)
        >>> m2
        Map({3: 6})

        Parameters
        ----------
        pred : ``(k, v) -> bool``
            predicate
        '''
        return Map((k, v) for k, v in self.items() if pred(k))

    def filter_by_value(self, pred):
        '''Create a new Map with values satisfying the predicate

        >>> m = Map({1: 2, 2: 4, 3: 6})
        >>> m2 = m.filter_by_value(lambda v: v % 3 == 0)
        >>> m2
        Map({3: 6})

        Parameters
        ----------
        pred : ``(k, v) -> bool``
            predicate
        '''
        return Map((k, v) for k, v in self.items() if pred(v))

    def group_by(self, key):
        '''Group key/value pairs into nested Maps.

        >>> Map(a=3, b=4, c=5).group_by(lambda k, v: v % 2)
        Map({1: Map({'a': 3, 'c': 5}), 0: Map({'b': 4})})

        Parameters
        ----------
        key : ``(k, v) -> key``
            predicate
        '''
        func = key
        grouped_d = defaultdict(Map)

        for key, value in self.items():
            grouped_d[func(key, value)][key] = value

        return Map(grouped_d)

    def reduce(self, key):
        pass

    def make_string(self,
                    key_value_format='{key!r}: {value!r}',
                    start='{', item_sep=', ', end='}'):
        '''Construct a string from key/values.

        >>> m = Map(a=3, b=4, c=5)
        >>> m.make_string()
        "{'a': 3, 'b': 4, 'c': 5}"
        >>> m.make_string(start='(', key_value_format='{key}={value!r}',
        ...               item_sep=', ', end=')')
        '(a=3, b=4, c=5)'

        Parameters
        ----------
        key_value_format : str
            string template using builtin ``str.format()`` for formatting
            key/value pairs. Default to ``'{key!r}: {value!r}'``.
            Available named placeholders: ``{key}``, ``{value}``
        start : str
            Default to ``'{'``.
        item_sep : str
            Default to ``', '``
        end : str
            Default to ``}``

        '''

        items_str = item_sep.join(
            key_value_format.format(key=key, value=value)
            for key, value in self.items())

        return start + items_str + end

    def take(self, n):
        '''create a Stream instance of first ``n`` ``Row(key, value)`` elements.

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.take(2).to_list()
        [Row(key='a', value=4), Row(key='b', value=5)]
        '''
        return self.to_stream().take(n)

    def first(self):
        '''Get the first item in ``Row(key, value)`` type

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.first()
        Row(key='a', value=4)
        >>> m.first().key
        'a'
        >>> m.first().value
        4
        >>> m = Map()
        >>> m.first()
        Traceback (most recent call last):
        ...
        IndexError: index out of range.
        '''
        return self.nth(0)

    def first_opt(self):
        '''Optionally get the first item.
        Return Some(Row(key, value)) if first item exists,
        otherwise return Nothing

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.first_opt().map(lambda kv: kv.transform(value=lambda v: v * 2))
        Some(Row(key='a', value=8))
        >>> m.first_opt().map(lambda kv: kv.value)
        Some(4)
        >>> m = Map()
        >>> m.first_opt()
        Nothing
        '''
        return self.nth_opt(0)

    def nth(self, index):
        '''Get the nth item in ``Row(key, value)`` type.

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.nth(2)
        Row(key='c', value=6)
        >>> m = Map(a=4, b=5)
        >>> m.nth(2)
        Traceback (most recent call last):
        ...
        IndexError: index out of range.

        '''
        try:
            key, value = next(itt.islice(self.items(), index, None))
            return KeyValue(key, value)
        except StopIteration:
            raise IndexError('index out of range.')

    def nth_opt(self, index):
        '''Optionally get the nth item.
        Return ``Some(Row(key, value))`` if first item exists,
        otherwise return Nothing.

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.first_opt().map(lambda kv: kv.transform(value=lambda v: v * 2))
        Some(Row(key='a', value=8))
        >>> m = Map()
        >>> m.first_opt()
        Nothing
        '''
        try:
            return Some(self.nth(index))
        except IndexError:
            return Nothing

    def len(self):
        '''Get the length of this Map

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.len()
        4
        '''
        return len(self)

    def to_stream(self):
        '''Create a Stream instance of ``Row(key, value)`` iterable.

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.to_stream().take(2).to_list()
        [Row(key='a', value=4), Row(key='b', value=5)]

        '''
        return Stream(self.items()).starmap(KeyValue)

    def to_array(self):
        '''Create a Array instance of ``Row(key, value)`` iterable.

        >>> m = Map(a=4, b=5, c=6, d=7)
        >>> m.to_array().take(2)
        Array([Row(key='a', value=4), Row(key='b', value=5)])

        '''
        return self.to_stream().to_array()

    def flip(self):
        '''Create a new Map which key/value pairs are fliped

        >>> m = Map(a=4, b=5, c=6)
        >>> m.flip()
        Map({4: 'a', 5: 'b', 6: 'c'})
        '''
        return Map((value, key) for key, value in self.items())


class FrozenMap(UserDict):

    def merge(self, others):
        pass

    def merge_with(self, others):
        pass

    def map(self, func):
        pass

    def map_keys(self):
        pass

    def map_values(self):
        pass

    def to_stream(self):
        pass

    def to_array(self):
        pass

    def project(self, keys):
        pass

    def flip(self):
        pass

    def get(self, key, default=None):
        pass

    def get_opt(self, key):
        pass

    def filter(self, pred):
        pass

    def filter_keys(self, pred):
        pass

    def filter_values(self, pred):
        pass

    def to_tuple(self):
        return tuple(self.items())
