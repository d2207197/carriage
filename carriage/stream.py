
import builtins
import functools as fnt
import heapq
import itertools as itt
import reprlib
from collections import Counter, defaultdict, deque

from .array import Array
from .monad import Monad
from .optional import Nothing, Some
from .repr import short_repr
from .row import CurrNext, CurrPrev, KeyValues, ValueIndex


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

    >>> strm = Stream(range(10))
    >>> strm = Stream([1, 2, 3])

    Some classmethods are provided for creating common Stream instances.

    >>> strm = Stream.range(0, 10, 2)
    >>> strm = Stream.count(0, 5)

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
    36
    >>> strm.to_list()
    [10, 12, 14]

    '''
    __slots__ = '_iterable', '_transformer'

    def __init__(self, iterable, transformer=None):
        '''Create a Stream from any iterable object.

        >>> strm = Stream([1,2,3])
        >>> strm = Stream(range(10, 15))
        >>> adict = {'a': 1, 'b': 2}
        >>> strm = Stream(adict.items())

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
        '''Create a Stream from range.

        >>> Stream.range(2, 10, 2).to_list()
        [2, 4, 6, 8]
        >>> Stream.range(3).to_list()
        [0, 1, 2]
        '''

        if end is None:
            start, end = 0, start

        return cls(range(start, end, step))

    @classmethod
    def count(cls, start, step=1):
        '''Create a infinite consecutive Stream

        >>> Stream.count(0, 3).take(3).to_list()
        [0, 3, 6]

        '''
        return cls(itt.count(start, step))

    @classmethod
    def repeat(cls, elems, times=None):
        '''Create a Stream repeating elems

        >>> Stream.repeat(1, 3).to_list()
        [1, 1, 1]
        >>> Stream.repeat([1, 2, 3], 2).to_list()
        [[1, 2, 3], [1, 2, 3]]
        '''
        return cls(itt.repeat(elems, times=times))

    @classmethod
    def cycle(cls, iterable):
        '''Create a Stream cycling a iterable

        >>> Stream.cycle([1,2]).take(5).to_list()
        [1, 2, 1, 2, 1]
        '''

        return cls(itt.cycle(iterable))

    @classmethod
    def repeatedly(cls, func, times=None):
        '''Create a Stream repeatedly calling a zero parameter function

        >>> def counter():
        ...     counter.num += 1
        ...     return counter.num
        >>> counter.num = -1
        >>> Stream.repeatedly(counter, 5).to_list()
        [0, 1, 2, 3, 4]
        '''
        def repeatedly_gen(times):
            while True:
                if times is None:
                    yield func()
                elif times > 0:
                    yield func()
                    times -= 1
                else:
                    return

        return cls(repeatedly_gen(times))

    @classmethod
    def iterate(cls, func, x):
        '''Create a Stream recursively applying a function to
        last return value.

        >>> def multiply2(x): return x * 2
        >>> Stream.iterate(multiply2, 3).take(4).to_list()
        [3, 6, 12, 24]
        '''
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

        >>> Stream.range(5, 10, 2).to_list()
        [5, 7, 9]

        Returns
        -------
        list
        '''
        return list(self)

    def to_series(self):
        '''Convert to a pandas Series

        >>> Stream.range(5, 10, 2).to_series()
        0    5
        1    7
        2    9
        dtype: int64

        Returns
        -------
        pandas.Series
        '''
        import pandas as pd
        return pd.Series(list(self))

    def to_set(self):
        '''Convert to a set

        >>> Stream.cycle([1, 2, 3]).take(5).to_set()
        {1, 2, 3}

        Returns
        -------
        set
        '''
        return set(self)

    def to_dict(self):
        '''Convert to a dict

        >>> Stream.range(5, 10, 2).zip_index().to_dict()
        {5: 0, 7: 1, 9: 2}

        Returns
        -------
        dict
        '''
        return dict(self)

    def to_map(self):
        '''Convert to a Map

        >>> Stream.range(5, 10, 2).zip_index().to_map()
        Map({5: 0, 7: 1, 9: 2})

        Returns
        -------
        Map
        '''
        from .map import Map
        return Map(self)

    def to_array(self):
        '''Convert to a Map

        >>> Stream.range(5, 8, 2).zip_index().to_array()
        Array([Row(value=5, index=0), Row(value=7, index=1)])

        Returns
        -------
        Array
        '''
        return Array(self)

    @as_stream
    def map(self, func):
        '''Create a new Stream by applying function to each element

        >>> Stream.range(5, 8).map(lambda x: x * 2).to_list()
        [10, 12, 14]

        Returns
        -------
        Stream
        '''
        return fnt.partial(map, func)

    @as_stream
    def starmap(self, func):
        '''Create a new Stream by evaluating function using argument tulpe
        from each element. i.e. ``func(*elem)``. It's convenient that
        if all elements in Stream are iterable and you want to treat
        each element in elemnts as separate argument while calling the
        function.

        >>> Stream([(1, 2), (3, 4)]).starmap(lambda a, b: a+b).to_list()
        [3, 7]
        >>> Stream([(1, 2), (3, 4)]).map(lambda a_b: a_b[0]+a_b[1]).to_list()
        [3, 7]
        '''
        return fnt.partial(itt.starmap, func)

    @as_stream
    def flatten(self):
        '''flatten each element

        >>> Stream([(1, 2), (3, 4)]).flatten().to_list()
        [1, 2, 3, 4]

        Returns
        -------
        Stream
        '''
        return itt.chain.from_iterable

    @as_stream
    def flat_map(self, to_iterable_func):
        '''Apply function to each element, then flatten the result.

        >>> Stream([1, 2, 3]).flat_map(range).to_list()
        [0, 0, 1, 0, 1, 2]

        Returns
        -------
        Stream
        '''

        def flat_map_tr(iterable):
            return itt.chain.from_iterable(map(to_iterable_func, iterable))
        return flat_map_tr

    @as_stream
    def tap(self, tag='', n=5, msg_format='{tag}:{index}: {elem}'):
        '''A debugging tool. This method create a new Stream with the same
        elements. While evaluating Stream, it print first n elements.

        >>> (Stream.range(3).tap('orig')
        ...  .map(lambda x: x * 2).tap_with(lambda i, e: f'{i} -> {e}')
        ...  .accumulate(lambda a, b: a + b).tap('acc')
        ...  .tap(msg_format='end\\n')
        ...  .to_list())
        orig:0: 0
        0 -> 0
        acc:0: 0
        end
        <BLANKLINE>
        orig:1: 1
        1 -> 2
        acc:1: 2
        end
        <BLANKLINE>
        orig:2: 2
        2 -> 4
        acc:2: 6
        end
        <BLANKLINE>
        [0, 2, 6]

        '''

        def tap_tr(self_):
            for index, elem in enumerate(self_):
                if index < n:
                    print(msg_format.format(tag=tag, index=index, elem=elem))
                yield elem
        return tap_tr

    @as_stream
    def tap_with(self, func, n=5):
        '''A debugging tool. This method create a new Stream with the same
        elements. While evaluating Stream, it call the function using
        index and element then prints the return value for first n elements.

        >>> (Stream.range(3).tap('orig')
        ...  .map(lambda x: x * 2).tap('x2')
        ...  .accumulate(lambda a, b: a + b).tap('acc')
        ...  .to_list())
        orig:0: 0
        x2:0: 0
        acc:0: 0
        orig:1: 1
        x2:1: 2
        acc:1: 2
        orig:2: 2
        x2:2: 4
        acc:2: 6
        [0, 2, 6]

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

        return tap_with_tr

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

    @reprlib.recursive_repr()
    def __repr__(self):
        if self._transformer is None:
            return (f'{type(self).__name__}'
                    f'({short_repr.repr(self._iterable)})')
        else:
            return (f'{type(self).__name__}'
                    f'({short_repr.repr(self._iterable)}, {self._transformer!r})')

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
        '''Create a new Stream of values by evaluating ``elem[key]`` for each
        element.'''
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        '''Create a new Stream of Optional values by evaluating ``elem[key]``
        for each element.
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

    def without(self, *elems):
        '''Create a new Stream without specified elements.'''
        try:
            elems = set(elems)
        except TypeError:
            # TODO: warn bad performance
            pass
        return self.filter(lambda elem: elem not in elems)

    @as_stream
    def filter(self, pred):
        '''Create a new Stream contains only elements passing predicate'''
        return fnt.partial(filter, pred)

    @as_stream
    def filter_false(self, pred):
        '''Create a new Stream contains only elements not passing predicate'''
        return fnt.partial(itt.filterfalse, pred)

    filterfalse = filter_false

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
    def reversed(self):
        '''Create a new reversed Stream.
        '''
        def reversed_tr(items):
            try:
                return reversed(items)
            except TypeError:
                return reversed(list(items))

        return reversed_tr

    @as_stream
    def sorted(self, key=None, reverse=False):
        '''Create a new sorted Stream.
        '''
        return fnt.partial(sorted, key=key, reverse=reverse)

    def sum(self):
        '''Get sum of elements'''
        return sum(self)

    def reduce(self, func):
        '''Apply a function of two arguments cumulatively to the elements
        in Stream from left to right.

        '''
        return fnt.reduce(func, self)

    def fold_left(self, func, initial):
        '''Apply a function of two arguments cumulatively to the elements
        in Stream from left to right.

        '''
        return fnt.reduce(func, self, initial)

    # def key_by(self, func):
    #     return self.map(lambda elem: Row(key=func(elem), value=elem))

    @as_stream
    def group_by(self, key=None):
        '''Create a new Stream using the builtin itertools.groupby,
        which sequentially groups elements as long as the key function
        evaluates to the same value.

        Comparing to ``group_by_as_map``, there're some pros and cons.

        Cons:

        - Elements should be sorted by the key function first,
          or elements with the same key may be broken into different groups.

        Pros:

        - Key function doesn't have to be evaluated to a hashable value.
          It can be any type which supports ``__eq__``.

        - Lazy-evaluating. Consume less memory while grouping.
          Yield a group as soon as possible.

        '''

        def group_by_tr(self_):
            for k, vs in itt.groupby(self_, key=key):
                yield KeyValues(key=k, values=Stream(vs))
        return group_by_tr

    groupby = group_by

    def group_by_as_map(self, key=None):
        '''Group values in to a Map by the value of key function evaluation
        result.

        Comparing to ``group_by``, there're some pros and cons.

        Pros:

        * Elements don't need to be sorted by the key function first.
          You can call ``map_group_by`` anytime and correct grouping result.

        Cons:

        * Key function has to be evaluated to a hashable value.

        * Not Lazy-evaluating. Consume more memory while grouping.
          Yield a group as soon as possible.
        '''

        from .map import Map
        key_to_grp = defaultdict(Array)
        for elem in self:
            key_to_grp[key(elem)].append(elem)
        return Map(key_to_grp)

    def multi_group_by_as_map(self, key=None):
        from .map import Map
        key_to_grp = defaultdict(list)
        for elem in self:
            for k in key(elem):
                key_to_grp[k].append(elem)
        return Map(key_to_grp)

    @as_stream
    def sliding_window(self, n):
        '''Create a new Stream instance that all elements are sliding windows
        of source elements.'''

        def sliding_window_tr(self_):
            self_itr = iter(self)
            dq = deque(itt.islice(self_itr, n - 1), maxlen=n)
            for item in self_itr:
                dq.append(item)
                yield tuple(dq)
        return sliding_window_tr

    def mean(self):
        '''Get the average of elements.

        >>> Array.range(10).mean()
        4.5
        '''
        length, summation = deque(enumerate(itt.accumulate(self), 1), 1).pop()
        return summation / length

    @as_stream
    def accumulate(self, func=None):
        '''Create a new Stream of calling ``itertools.accumulate``'''
        return fnt.partial(itt.accumulate, func=func)

    def value_counts(self):
        '''Get a Counter instance of elements counts'''
        return Counter(self)

    @as_stream
    def extended(self, iterable):
        '''Create a new Stream that extends source Stream with another
        iterable'''

        def extended_tr(self_):
            return itt.chain(self_, iterable)
        return extended_tr

    def appended(self, elem):
        '''Create a new Stream that extends source Stream with another element.
        '''

        return self.extended((elem,))

    @as_stream
    def distincted(self):
        '''Create a new Stream with non-repeating elements. And elements are
        with the same order of first occurence in the source Stream.

        '''
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

    @as_stream
    def permutations(self, r=None):
        return fnt.partial(itt.permutations, r=r)

    @as_stream
    def combinations(self, r):
        return fnt.partial(itt.combinations, r=r)

    @as_stream
    def combinations_with_replacement(self, r):
        return fnt.partial(itt.combinations_with_replacement, r=r)

    @as_stream
    def nsmallest(self, n, key=None):
        '''Get the n smallest elements.

        >>> Stream([1, 5, 2, 3, 6]).nsmallest(2).to_list()
        [1, 2]

        '''

        def nsmallest_tr(self_):
            return heapq.nsmallest(n, iter(self_), key=key)
        return nsmallest_tr

    @as_stream
    def nlargest(self, n, key=None):
        '''Get the n largest elements.

        >>> Stream([1, 5, 2, 3, 6]).nlargest(2).to_list()
        [6, 5]
        '''

        def nlargest_tr(self_):
            return heapq.nlargest(n, iter(self_), key=key)
        return nlargest_tr

    def tee(self, n=2):
        '''Copy the Stream into multiple Stream with the same elements.

        >>> itr = iter(range(3, 6))
        >>> s1 = Stream(itr).map(lambda x: x * 2)
        >>> s2, s3 = s1.tee(2)
        >>> s2.map(lambda x: x * 2).to_list()
        [12, 16, 20]
        >>> s3.map(lambda x: x * 3).to_list()
        [18, 24, 30]

        '''
        itrs = itt.tee(self, 2)
        return tuple(map(Stream, itrs))

    # def copy(self):
    #     return Array(copy(self._items))

    def grouped(self):
        # TODO
        pass

    def for_each(self):
        pass
