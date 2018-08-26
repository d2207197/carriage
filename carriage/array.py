
import builtins
import collections
import itertools as itt
from collections import Counter, defaultdict, deque
from copy import copy

from .monad import Monad
from .optional import Nothing, Some
from .repr import short_repr
from .row import CurrNext, CurrPrev, KeyValues, ValueIndex


class Array(Monad):
    __slots__ = '_items'

    @classmethod
    def range(cls, start, end=None, step=1):
        '''Create a Array from range.

        >>> Array.range(2, 10, 2).to_list()
        [2, 4, 6, 8]
        >>> Array.range(3).to_list()
        [0, 1, 2]
        '''
        if end is None:
            start, end = 0, start

        return cls(range(start, end, step))

    @property
    def _base_type(self):
        return Array

    def __init__(self, items=None):
        '''Create a Array object

        >>> Array()
        Array([])
        >>> Array([1, 2, 3])
        Array([1, 2, 3])
        >>> Array(range(2, 8, 2))
        Array([2, 4, 6])

        '''

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

    def to_list(self, copy=False):
        '''Convert to a list.

        >>> Array.range(3).to_list()
        [0, 1, 2]
        '''

        if copy:
            return self._items
        else:
            return self._items[:]

    def to_series(self):
        '''Convert to a pandas Series

        >>> Array.range(5, 10, 2).to_series()
        0    5
        1    7
        2    9
        dtype: int64

        Returns
        -------
        pandas.Series
        '''
        import pandas as pd
        return pd.Series(self)

    def to_set(self):
        '''Convert to a set

        >>> Array([3, 2, 3, 6, 2]).to_set()
        {2, 3, 6}

        Returns
        -------
        set
        '''
        return set(self)

    def to_dict(self):
        '''Convert to a dict

        >>> Array.range(5, 10, 2).zip_index().to_dict()
        {5: 0, 7: 1, 9: 2}

        Returns
        -------
        dict
        '''
        return dict(self)

    def to_map(self):
        '''Convert to a Map

        >>> Array.range(5, 10, 2).zip_index().to_map()
        Map({5: 0, 7: 1, 9: 2})

        Returns
        -------
        Map
        '''
        from .map import Map
        return Map(self)

    def to_stream(self):
        '''Convert to a Stream

        >>> strm = Array.range(5, 8, 2).zip_index().to_stream()
        >>> type(strm)
        <class 'carriage.stream.Stream'>
        >>> strm.to_array()
        Array([Row(value=5, index=0), Row(value=7, index=1)])

        Returns
        -------
        Stream
        '''
        from .stream import Stream
        return Stream(self)

    def map(self, action):
        '''Create a new Array by applying function to each element

        >>> Array.range(5, 8).map(lambda x: x * 2)
        Array([10, 12, 14])

        Returns
        -------
        Array
        '''
        return Array(action(item) for item in self)

    def starmap(self, func):
        '''Create a new Array by evaluating function using argument tulpe
        from each element. i.e. ``func(*elem)``. It's convenient that
        if all elements in Array are iterable and you want to treat
        each element in elemnts as separate argument while calling the
        function.

        >>> Array([(1, 2), (3, 4)]).starmap(lambda a, b: a+b)
        Array([3, 7])

        The map way. Not easy to read and write

        >>> Array([(1, 2), (3, 4)]).map(lambda a_b: a_b[0]+a_b[1])
        Array([3, 7])
        '''
        return Array(itt.starmap(func, self))

    def flatten(self):
        '''flatten each element

        >>> Array([(1, 2), (3, 4)]).flatten()
        Array([1, 2, 3, 4])

        Returns
        -------
        Array
        '''
        return Array(itt.chain.from_iterable(self._items))

    def flat_map(self, to_iterable_action):
        '''Apply function to each element, then flatten the result.

        >>> Array([1, 2, 3]).flat_map(range)
        Array([0, 0, 1, 0, 1, 2])

        Returns
        -------
        Array
        '''
        return Array(
            itt.chain.from_iterable(
                to_iterable_action(item)
                for item in self._items))

    def tap(self, tag='', n=5, msg_format='{tag}:{index}: {elem}'):
        '''A debugging tool. This method create a new Array with the same
        elements. While creating it, it print first n elements.


        >>> (Array.range(3).tap('orig')
        ...  .map(lambda x: x * 2).tap('x2')
        ...  .accumulate(lambda a, b: a + b)
        ...  .tap_with(func=lambda i, e: f'{i} -> {e}')
        ... )
        orig:0: 0
        orig:1: 1
        orig:2: 2
        x2:0: 0
        x2:1: 2
        x2:2: 4
        0 -> 0
        1 -> 2
        2 -> 6
        Array([0, 2, 6])

        '''

        def tap_tr(self_):
            for index, elem in enumerate(self_):
                if index < n:
                    print(msg_format.format(tag=tag, index=index, elem=elem))
                yield elem
        return Array(tap_tr(self))

    def tap_with(self, func, n=5):
        '''A debugging tool. This method create a new Array with the same
        elements. While creating Array, it call the function using
        index and element then prints the return value for first n elements.


        >>> (Array.range(3).tap('orig')
        ...  .map(lambda x: x * 2).tap('x2')
        ...  .accumulate(lambda a, b: a + b)
        ...  .tap_with(func=lambda i, e: f'{i} -> {e}')
        ... )
        orig:0: 0
        orig:1: 1
        orig:2: 2
        x2:0: 0
        x2:1: 2
        x2:2: 4
        0 -> 0
        1 -> 2
        2 -> 6
        Array([0, 2, 6])

        Parameters
        -----------
        func : ``func(index, elem) -> Any``
            Function for building the printing object.
        n : int
            First n element will be print.
        '''

        def tap_with_tr(self_):
            for index, elem in enumerate(self_):
                if index < n:
                    print(func(index, elem))
                yield elem

        return Array(tap_with_tr(self))

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
        return f'{type(self).__name__}({short_repr.repr(self._items)})'

    @property
    def _comparing_value(self):
        return self._items

    def len(self):
        '''Get the length'''
        return len(self)

    def __getitem__(self, index):
        '''Get the item in the nth position if index is integer.
        Get a Array of a slice of items if index is a slice object.

        Parameters
        ----------
        index : int, slice
            index of target item or a slice object
        '''
        if isinstance(index, slice):
            return Array(self._items[index])
        return self._items[index]

    def get(self, index, default=None):
        '''Get item of the index. Return default value if not exists.
        '''
        if index < len(self):
            return self._items[index]
        return default

    def get_opt(self, index):
        '''Optionally get item of the index.
        Return Some(value) if exists.
        Otherwise return Nothing.
        '''
        if (index if index >= 0 else abs(index) - 1) < len(self):
            return Some(self._items[index])

        return Nothing

    def slice(self, start, stop, step=None):
        '''Create a Array from the slice of items.

        Returns
        -------
        Array
        '''
        return self[slice(start, stop, step)]

    def first(self):
        '''Get first element
        '''
        return self._items[0]

    def second(self):
        '''Get second element
        '''
        return self._items[1]

    def last(self):
        '''Get last element
        '''
        return self._items[-1]

    def first_opt(self):
        '''Get first element as Some(element), or Nothing if not exists
        '''
        return self.get_opt(0)

    def second_opt(self):
        '''Get second element as Some(element), or Nothing if not exists
        '''
        return self.get_opt(1)

    def last_opt(self):
        '''Get last element as Some(element), or Nothing if not exists
        '''
        return self.get_opt(-1)

    def find(self, pred):
        '''Get first element satifying predicate
        '''
        for item in self._items:
            if pred(item):
                return item

    def find_opt(self, pred):
        '''Optionally get first element satifying predicate.
        Return Some(element) if exist
        Otherwise return Nothing
        '''
        for item in self._items:
            if pred(item):
                return Some(item)

        else:
            return Nothing

    def take(self, n):
        '''Create a new Array of only first n element '''
        return Array(self._items[:n])

    def drop(self, n):
        '''Create a new Array of first n element dropped
        '''
        return Array(self._items[n:])

    def tail(self):
        '''Create a new Array first element dropped
        '''
        return Array(self._items[1:])

    def butlast(self):
        '''Create a new Array that last element dropped
        '''
        return self[:-1]

    def take_right(self, n):
        '''Create a new Array with last n elements
        '''
        return Array(self._items[-n:])

    takeright = take_right

    def drop_right(self, n):
        '''Create a new Array that last n elements dropped
        '''
        return Array(self._items[:-n])

    dropright = drop_right

    def take_while(self, pred):
        '''Create a new Array with successive elements as long as
        predicate evaluates to true.
        '''
        return Array(itt.takewhile(pred, self._items))

    takewhile = take_while

    def drop_while(self, pred):
        '''Create a new Array without elements as long as predicate
        evaluates to true.
        '''
        return Array(itt.dropwhile(pred, self._items))

    dropwhile = drop_while

    def split_before(self, pred):
        '''Create a new Array of Arrays by splitting before each element
        passing predicate.
        '''
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
        '''Create a new Array of Arrays by splitting after each element
        passing predicate.
        '''
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
        '''Create a new Array of values by evaluating ``elem[key]`` for each
        element.'''
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        '''Create a new Array of Optional values by evaluating ``elem[key]``
        for each element.
        Get ``Some(value)`` if the key exists for that element, otherwise get
        Nothing singleton.
        '''
        return self.map(lambda d: Some(d[key])
                        if key in d else Nothing)

    def pluck_attr(self, attr):
        '''Create a new Array of Optional values by evaluating ``elem.attr`` of
        each element.
        Get ``Some(value)`` if attr exists for that element, otherwise get
        Nothing singleton.
        '''
        return self.map(lambda obj: getattr(obj, attr))

    def without(self, *items):
        '''Create a new Array without specified elements.'''
        items = set(items)
        return self.filter(lambda item: item not in items)

    def filter(self, pred):
        '''Create a new Array contains only elements passing predicate'''
        return Array(builtins.filter(pred, self._items))

    def filter_false(self, pred):
        '''Create a new Array contains only elements not passing predicate'''
        return Array(itt.filterfalse(pred, self._items))

    filterfalse = filter_false

    def where(self, **conds):
        '''Create a new Array contains only mapping pass all conditions.
        '''
        return self.filter(lambda d:
                           all(key in d and d[key] == value
                               for key, value in conds.items()))

    def interpose(self, sep):
        '''Create a new Array by interposing separater between elemens.
        '''
        # TODO
        for item in self._items:
            yield item
            yield

    def zip(self, *iterable):
        '''Create a new Array by zipping elements with other iterables.
        '''
        return Array(zip(self._items, *iterable))

    def zip_longest(self, *iterables, fillvalue=None):
        '''Create a new Array by zipping elements with other iterables
        as long as possible.
        '''
        return Array(itt.zip_longest(
            self._items, *iterables,
            fillvalue=fillvalue))

    def zip_longest_opt(self, *iterables):
        iterables = [map(Some, it) for it in iterables]
        return Array(itt.zip_longest(map(Some, self._items),
                                     *iterables,
                                     fillvalue=Nothing))

    def zip_next(self, fillvalue=None):
        '''Create a new Array by zipping elements with next one.
        '''
        items_itr = iter(self._items)
        next(items_itr)
        nexts = itt.chain(items_itr, [fillvalue])
        return Array(itt.starmap(CurrNext, zip(self._items, nexts)))

    def zip_prev(self, fillvalue=None):
        '''Create a new Array by zipping elements with previous one.
        '''
        prevs = itt.chain([fillvalue], self._items)
        return Array(itt.starmap(CurrPrev, zip(self._items, prevs)))

    def zip_index(self, start=0):
        '''Create a new Array by zipping elements with index.
        '''
        return Array(itt.starmap(ValueIndex,
                                 zip(self._items, itt.count(start))))

    def reverse(self):
        '''In place reverse this Array.
        '''
        self._items.reverse()
        return self

    def reversed(self):
        '''Create a new reversed Array.
        '''
        return Array(reversed(self._items))

    def sort(self, key=None, reverse=False):
        '''In place sort this Array.
        '''
        self._items.sort(key=key, reverse=reverse)
        return self

    def sorted(self, key=None, reverse=False):
        '''Create a new sorted Array.
        '''
        return Array(sorted(self._items, key=key, reverse=reverse))

    def sum(self):
        '''Get sum of elements'''
        return sum(self)

    def reduce(self):
        # TODO
        pass

    def group_by(self, key=None):
        '''Create a new Array using the builtin itertools.groupby,
        which sequentially groups elements as long as the key function
        evaluates to the same value.

        Comparing to ``group_by_as_map``, there're some pros and cons.

        Cons:

        - Elements should be sorted by the key function first,
          or elements with the same key may be broken into different groups.

        Pros:

        - Key function doesn't have to be evaluated to a hashable value.
          It can be any type which supports ``__eq__``.

        '''

        def group_by_tr(self_):
            for k, vs in itt.groupby(self_, key=key):
                yield KeyValues(key=k, values=Array(vs))
        return Array(group_by_tr(self))

    def group_by_as_map(self, key=None):
        '''Group values in to a Map by the value of key function evaluation
        result.

        Comparing to ``group_by``, there're some pros and cons.

        Pros:

        * Elements don't need to be sorted by the key function first. 
          You can call ``map_group_by`` anytime and correct grouping result.

        Cons:

        * Key function has to be evaluated to a hashable value.

        '''

        from .map import Map
        key_to_grp = defaultdict(Array)
        for elem in self:
            key_to_grp[key(elem)].append(elem)
        return Map(key_to_grp)

    def accumulate(self, func=None):
        '''Create a new Array of calling ``itertools.accumulate``'''
        return Array(itt.accumulate(self._items, func))

    def mean(self):
        '''Get the average of elements.'''

        return sum(self) / len(self)

    def sliding_window(self, n):
        '''Create a new Array instance that all elements are sliding windows
        of source elements.'''

        def sliding_window_tr(self_):
            self_itr = iter(self)
            dq = deque(itt.islice(self_itr, n - 1), maxlen=n)
            for item in self_itr:
                dq.append(item)
                yield tuple(dq)
        return Array(sliding_window_tr(self))

    def value_counts(self):
        '''Get a Counter instance of elements counts'''
        return Counter(self)

    def extend(self, iterable):
        '''Extend the Array from iterable'''
        self._items.extend(iterable)
        return self

    def extended(self, iterable):
        '''Create a new Array that extends source Array with another
        iterable'''
        alist = self.copy()
        alist.extend(iterable)
        return alist

    def append(self, item):
        '''Append element to the Array'''
        self._items.append(item)
        return self

    def appended(self, item):
        '''Create a new Array that extends source Array with another element.
        '''
        alist = self.copy()
        alist.append(item)
        return alist

    def distincted(self):
        '''Create a new Array with non-repeating elements. And elements are
        with the same order of first occurence in the source Array.

        '''
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

    def make_string(self,
                    elem_format='{elem!r}',
                    start='[', elem_sep=', ', end=']'):
        '''Make string from elements

        >>> Array.range(5, 8).make_string()
        '[5, 6, 7]'
        >>> print(Array.range(5, 8).make_string(elem_sep='\\n', start='', end='', elem_format='{index}: {elem}'))
        0: 5
        1: 6
        2: 7
        '''

        elems_str = elem_sep.join(elem_format.format(index=idx, elem=elem)
                                  for idx, elem in enumerate(self))
        return start + elems_str + end
