import functools as fnt
import itertools as itt

from tabulate import tabulate, tabulate_formats

from .row import Row
from .stream import Stream, as_stream


class StreamTable(Stream):
    '''StreamTable is similar to Stream but designed to work on Rows only.
    '''

    def __init__(self, iterable, *, pipeline=None):
        '''Create a StreamTable from an iterable object of Rows

        >>> stb = StreamTable([Row(x=1, y=3), Row(x=2, y=4)])
        >>> stb.show()
        |   x |   y |
        |-----+-----|
        |   1 |   3 |
        |   2 |   4 |

        '''

        Stream.__init__(self, iterable, pipeline=pipeline)

    @classmethod
    def range(cls, start, end=None, step=1):
        '''Create a StreamTable from range

        >>> StreamTable.range(1, 10, 3).show()
        |   range |
        |---------|
        |       1 |
        |       4 |
        |       7 |
        '''
        strm = Stream.range(start, end, step).map(lambda elem: Row(range=elem))
        return cls(strm)

    @classmethod
    def count(cls, start, step=1):
        '''Create a inifinite consecutive StreamTable

        >>> StreamTable.count(3, 5).take(3).show()
        |   count |
        |---------|
        |       3 |
        |       8 |
        |      13 |

        '''
        strm = Stream.count(start, step).map(lambda elem: Row(count=elem))
        return cls(strm)

    @classmethod
    def repeat(cls, elems, times=None):
        '''Create a StreamTable repeating elems

        >>> StreamTable.repeat(1, 3).show()
        |   repeat |
        |----------|
        |        1 |
        |        1 |
        |        1 |
        '''
        strm = Stream.repeat(elems, times).map(lambda elem: Row(repeat=elem))
        return cls(strm)

    @classmethod
    def cycle(cls, iterable):
        '''Create a StreamTable cycling a iterable

        >>> StreamTable.cycle([1,2]).take(5).show()
        |   cycle |
        |---------|
        |       1 |
        |       2 |
        |       1 |
        |       2 |
        |       1 |
        '''

        strm = Stream.cycle(iterable).map(lambda elem: Row(cycle=elem))
        return cls(strm)

    @classmethod
    def repeatedly(cls, func, times=None):
        '''Create a StreamTable repeatedly calling a zero parameter function

        >>> def counter():
        ...     counter.num += 1
        ...     return counter.num
        >>> counter.num = -1
        >>> StreamTable.repeatedly(counter, 5).show()
        |   repeatedly |
        |--------------|
        |            0 |
        |            1 |
        |            2 |
        |            3 |
        |            4 |
        '''
        strm = Stream.repeatedly(func, times).map(
            lambda elem: Row(repeatedly=elem))
        return cls(strm)

    @classmethod
    def iterate(cls, func, x):
        '''Create a StreamTable recursively applying a function to
        last return value.

        >>> def multiply2(x): return x * 2
        >>> StreamTable.iterate(multiply2, 3).take(4).show()
        |   iterate |
        |-----------|
        |         3 |
        |         6 |
        |        12 |
        |        24 |
        '''
        strm = Stream.iterate(func, x).map(lambda elem: Row(iterate=elem))
        return cls(strm)

    @classmethod
    def from_dataframe(cls, df, with_index=False):
        '''Create from Pandas DataFrame

        >>> import pandas as pd
        >>> df = pd.DataFrame([(0, 1), (2, 3)], columns=['a', 'b'])
        >>> StreamTable.from_dataframe(df).show()
        |   a |   b |
        |-----+-----|
        |   0 |   1 |
        |   2 |   3 |

        Parameters
        ----------
        df : pandas.DataFrame
            source DataFrame
        with_index : bool
            include index value or not

        Returns
        -------
        StreamTable

        '''
        rows = Stream(df.itertuples())
        rows = rows.map(lambda t: Row.from_values(t, fields=t._fields))

        if not with_index:
            rows = rows.map(lambda row: row.without('Index'))

        return cls(rows.to_list())

    @classmethod
    def from_tuples(cls, tuples, fields=None):
        '''Create from iterable of tuple

        >>> StreamTable.from_tuples([(1, 2), (3, 4)], fields=('x', 'y')).show()
        |   x |   y |
        |-----+-----|
        |   1 |   2 |
        |   3 |   4 |

        Parameters
        ----------
        tuples : Iterable[tuple]
            data
        fields : Tuple[str]
            field names

        '''
        stm = Stream(tuples).tuple_as_row(fields=fields)
        return cls(stm)

    def to_dataframe(self):
        '''Convert to Pandas DataFrame

        Returns
        -------
        pandas.DataFrame
        '''
        import pandas as pd
        rows = self.to_list()
        fields = self._scan_fields(rows[:10])
        return pd.DataFrame(rows, columns=fields)

    def to_stream(self):
        '''Convert to Stream

        Returns
        -------
        Stream
        '''
        return Stream(self)

    def to_dicts(self):
        return self.map(lambda row: row.to_dict()).to_list()

    def show(self, n=10, tablefmt='orgtbl'):
        '''print rows

        Parameters
        ----------
        n : int
            number of rows to show
        tablefmt : str
            output table format.
            all possible format strings are in `tabulate.tabulate_formats`
        '''
        print(self.tabulate(n=n, tablefmt=tablefmt))

    def tabulate(self, n=10, tablefmt='orgtbl'):
        '''return tabulate formatted string

        Parameters
        ----------
        n : int
            number of rows to show
        tablefmt : str
            output table format.
            all possible format strings are in `StreamTable.tabulate.tablefmts``
        '''
        rows = list(itt.islice(self, 0, n))
        header_fields = self._scan_fields(rows)
        return tabulate(
            rows,
            headers=header_fields,
            tablefmt=tablefmt)

    @as_stream
    def select(self, *fields, **field_funcs):
        '''Assume elements in Stream is in Row type and
        create a new Stream by keeping only specified fields in each Row

        >>> from carriage import Row, X
        >>> st = StreamTable([Row(x=3, y=4), Row(x=-1, y=2)])
        >>> st.select('x', z=X.x + X.y, pi=3.14).to_list()
        [Row(x=3, z=7, pi=3.14), Row(x=-1, z=1, pi=3.14)]

        Parameters
        ----------
        *fields : List[str]
            fields to keep
        **field_funcs : Map[str, Function or scalar]
            If value is a function, this function will be evaluated with the current row as the only argument.
            If value is not callable, use the value directly.

        Returns
        -------
        StreamTable
        '''
        return fnt.partial(
            map,
            lambda row:
            row.evolve(**{field: func(row) if callable(func) else func
                          for field, func in field_funcs.items()})
            .project(*fields, *field_funcs.keys()))

    @as_stream
    def where(self, *conds, **kwconds):
        '''Create a new Stream contains only Rows pass all conditions.

        >>> from carriage import Row, X
        >>> st = StreamTable([Row(x=3, y=4), Row(x=3, y=5), Row(x=4, y=5)])
        >>> st.where(x=3).to_list()
        [Row(x=3, y=4), Row(x=3, y=5)]
        >>> st.where(X.y > 4).to_list()
        [Row(x=3, y=5), Row(x=4, y=5)]

        Returns
        -------
        StreamTable

        '''
        return fnt.partial(
            filter,
            lambda row:
            all(cond(row) for cond in conds) and
            all(getattr(row, field) == value
                for field, value in kwconds.items()))

    @classmethod
    def _scan_fields(cls, rows):
        all_fields = []
        all_fields_set = set()
        for row in rows:
            missing_fields = set(row.fields()) - all_fields_set
            for field in row.fields():
                if field in missing_fields:
                    all_fields.append(field)

            all_fields_set.update(missing_fields)

        return all_fields

    def _repr_html_(self):
        return self.tabulate(tablefmt='html')

    def _repr_str_(self):
        return self.tabulate(tablefmt='orgtbl')


StreamTable.tabulate.tablefmts = tabulate_formats
