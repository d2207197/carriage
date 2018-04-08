
import builtins
import functools as fnt
import heapq
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

    wraped.call = f

    return wraped


class Stream(Monad):
    '''An iterable wrapper for building a lazy-evaluating sequence
    transformation pipeline.


    Stream is initiated by providing any iterable object like list, tuple,
    iterator and even an infinite one.

    >>> strm = Stream(iterable)
    >>> strm = Stream([1, 2, 3])

    Some classmethods are provided for creating common Stream instances.

    >>> strm = Stream.range(start, stop, step)
    >>> strm = Stream.count(start, step)

    Stream instance is immutable. Calling a transforamtion function would
    create a new Stream instance everytime. But don't worry, because of
    it's lazy-evaluating characteristic, no duplicated data are generated.

    >>> strm1 = Stream.range(5, 10)
    >>> strm2 = strm1.map(lambda n: n * 2)
    >>> strm3 = strm1.map(lambda n: n * 3)
    >>> strm1 is strm2 or strm1 is strm3 or strm2 is strm3
    False

    To evaluate a Stream instance, call an action function.
    >>> strm = Stream.range(5, 10).map(lambda n: n * 2).take(3)
    >>> strm.sum()
    3

    '''
    __slots__ = '_iterable', '_transformer'

    def __init__(self, iterable, transformer=None):
        '''Create a Stream from any iterable object.

        Parameters
        ----------
        iterable : any iterable. list, tuple, iterator
            Input iterable object.
        transformer : function of type ``iterable -> iterable``
            This is for internal use only.
        '''

        self._iterable = iterable
        self._transformer = transformer

    @classmethod
    def range(cls, start, end=None, step=1):
        '''Create a Stream from range.'''

        if end is None:
            start, end = 0, start

        return cls(range(start, end, step))

    @classmethod
    def count(cls, start, step=1):
        '''Create a infinite consecutive Stream'''
        return cls(itt.count(start, step))

    @classmethod
    def repeat(cls, elems, times=None):
        '''Create a Stream repeating elems'''
        return cls(itt.repeat(elems, times=times))

    @classmethod
    def cycle(cls, iterable):
        '''Create a Stream cycling a iterable'''
        return cls(itt.cycle(iterable))

    @classmethod
    def repeatedly(cls, func, times=None):
        '''Create a Stream repeatedly calling a zero parameter function'''
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
        '''Create a Stream recursively applying a function to
        last return value.'''
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
        '''Convert to a list.

        Returns
        -------
        list
        '''
        return list(self)

    @as_stream
    def flat_map(self, to_iterable_func):
        '''Apply function to each element, then flatten the result.

        Returns
        -------
        Stream
        '''

        def flat_map_tr(iterable):
            return itt.chain.from_iterable(map(to_iterable_func, iterable))
        return flat_map_tr

    @as_stream
    def map(self, func):
        '''Apply function to each element

        Returns
        -------
        Stream
        '''
        return fnt.partial(map, func)

    @as_stream
    def flatten(self):
        '''flatten each element

        Returns
        -------
        Stream
        '''
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
        '''Get the length of the Stream'''
        return sum(1 for item in self)

    @classmethod
    def _check_index_range(cls, index):
        if index is not None and index < 0:
            raise ValueError(
                'Stream index should be greater than 0. '
                'Be aware of that indexing an iterator would '
                'consume items from it.')

    def __getitem__(self, index):
        '''Get the item in the nth position if index is integer.
        Get a Stream of a slice of items if index is a slice object.

        Be aware of that if the source iterable is an iterator, you might get
        different item for the index if you call multiple times.

        Parameters
        ----------
        index : int, slice
            index of target item or a slice object
        '''

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
        '''Get item of the index. Return default value if not exists.
        '''
        # TODO: support negative index
        # dd = deque(aa, maxlen=1)

        self._check_index_range(index)
        return next(itt.islice(self, index, None), default)

    def get_opt(self, index):
        '''Optionally get item of the index.
        Return Some(value) if exists.
        Otherwise return Nothing.
        '''
        try:
            return Some(self[index])
        except IndexError:
            return Nothing

    @as_stream
    def slice(self, start, stop, step=None):
        '''Create a Stream from the slice of items.

        Returns
        -------
        Stream
        '''
        self._check_index_range(start)
        self._check_index_range(stop)
        return lambda iterable: itt.islice(iterable, start, stop, step)

    def first(self):
        '''Get first element
        '''
        return self[0]

    def second(self):
        '''Get second element
        '''
        return self[1]

    def last(self):
        '''Get last element
        '''
        return deque(self, 1)[-1]

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
        dq = deque(self, 1)
        if len(dq) > 0:
            return Some(dq[-1])

        return Nothing

    def find(self, pred):
        '''Get first element satifying predicate
        '''
        for item in self:
            if pred(item):
                return item

    def find_opt(self, pred):
        '''Optionally get first element satifying predicate.
        Return Some(element) if exist
        Otherwise return Nothing
        '''
        for item in self:
            if pred(item):
                return Some(item)

        else:
            return Nothing

    def take(self, n):
        '''Create a new Stream contains only first n element
        '''
        return self[:n]

    def drop(self, n):
        '''Create a new Stream with first n element dropped
        '''
        return self[n:]

    def tail(self):
        '''Create a new Stream with first element dropped
        '''
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
    def take_while(self, pred):
        '''Create a new Stream with successive elements as long as
        predicate evaluates to true.
        '''
        return fnt.partial(itt.takewhile, pred)

    takewhile = take_while

    @as_stream
    def drop_while(self, pred):
        '''Create a new Stream without elements as long as predicate
        evaluates to true.
        '''
        return fnt.partial(itt.dropwhile, pred)

    dropwhile = drop_while

    @as_stream
    def split_before(self, pred):
        '''Create a new Stream of Arrays by splitting before each element
        passing predicate.
        '''
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
        '''Create a new Stream of Arrays by splitting after each element
        passing predicate.
        '''
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
        '''Create a new Stream of values by evaluating ``elem[key]`` of each
        element.'''
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        '''Create a new Stream of Optional values by evaluating ``elem[key]`` of
        each element.
        Get ``Some(value)`` if the key exists for that element, otherwise get
        Nothing singleton.
        '''
        return self.map(lambda d: Some(d[key])
                        if key in d else Nothing)

    def pluck_attr(self, attr):
        '''Create a new Stream of Optional values by evaluating ``elem.attr`` of
        each element.
        Get ``Some(value)`` if attr exists for that element, otherwise get
        Nothing singleton.
        '''
        return self.map(lambda obj: getattr(obj, attr))

    @as_stream
    def filter(self, pred):
        '''Create a new Stream contains only elements passing predicate'''
        return fnt.partial(filter, pred)

    @as_stream
    def filter_false(self, pred):
        '''Create a new Stream contains only elements not passing predicate'''
        return fnt.partial(itt.filterfalse, pred)

    filterfalse = filter_false

    def without(self, *elems):
        '''Create a new Stream without specified elements.'''
        try:
            elems = set(elems)
        except TypeError:
            # TODO: warn bad performance
            pass
        return self.filter(lambda elem: elem not in elems)

    def where(self, **conds):
        '''Create a new Stream contains only mapping pass all conditions.

        '''
        return self.filter(lambda d:
                           all(key in d and d[key] == value
                               for key, value in conds.items()))

    @as_stream
    def interpose(self, sep):
        '''Create a new Stream by interposing separater between elemens.
        '''
        def interpose_tr(iterable):
            iterator = iter(iterable)
            yield next(iterator)
            for item in iterator:
                yield sep
                yield item

        return interpose_tr

    @as_stream
    def zip(self, *iterables):
        '''Create a new Stream by zipping elements with other iterables.
        '''
        def zip_tr(items):
            return builtins.zip(items, *iterables)

        return zip_tr

    @as_stream
    def zip_longest(self, *iterables, fillvalue=None):
        '''Create a new Stream by zipping elements with other iterables
        as long as possible.
        '''
        def zip_longest_tr(items):
            return itt.zip_longest(items, *iterables, fillvalue=fillvalue)
        return zip_longest_tr

    @as_stream
    def zip_prev(self, fillvalue=None):
        '''Create a new Stream by zipping elements with previous one.
        '''
        def zip_prev_tr(items):
            items, prevs = itt.tee(items)
            prevs = itt.chain([fillvalue], prevs)
            return itt.starmap(CurrPrev, builtins.zip(items, prevs))
        return zip_prev_tr

    @as_stream
    def zip_next(self, fillvalue=None):
        '''Create a new Stream by zipping elements with next one.
        '''
        def zip_next_tr(items):
            items, nexts = itt.tee(items)
            next(nexts, None)
            return itt.starmap(
                CurrNext, itt.zip_longest(items, nexts, fillvalue=fillvalue))
        return zip_next_tr

    def zip_index(self, start=0):
        '''Create a new Stream by zipping elements with index.
        '''
        return self.zip(itt.count(start)).starmap(ValueIndex)

    @as_stream
    def starmap(self, func):
        return fnt.partial(itt.starmap, func)

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

    @as_stream
    def nsmallest(self, n, key=None):
        def nsmallest_tr(self_):
            return heapq.nsmallest(n, iter(self_), key=key)
        return nsmallest_tr

    @as_stream
    def nlargest(self, n, key=None):
        def nlargest_tr(self_):
            return heapq.nlargest(n, iter(self_), key=key)
        return nlargest_tr

    def tee(self, n=2):
        itrs = itt.tee(self, n=2)
        return tuple(map(Stream, itrs))

    @as_stream
    def tap(self, n=5, tag='', msg_format='{tag}:{index}: {elem}'):
        def tap_tr(self_):
            for index, elem in enumerate(self_):
                if index < n:
                    print(msg_format.format(tag=tag, index=index, elem=elem))
                yield elem
        return tap_tr

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

    def grouped(self):
        pass
