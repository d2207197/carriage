import functools as fnt
import io
import itertools as itt
import json
from pathlib import Path

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

    @classmethod
    def read_jsonl(cls, path):
        '''Create from a jsonlines file

        >>> StreamTable.read_jsonl('person.jsonl') # doctest: +SKIP
        |   name |   age |
        |--------+-------|
        |   john |    18 |
        |   jane |    26 |

        Parameters
        ----------
        path : str or path or file object
            path to the input file

        '''
        from carriage import Row

        if isinstance(path, io.TextIOBase):
            f = path
        else:
            f = Path(path).open('rt')

        stm = (Stream(f)
               .map(json.loads)  # dicts
               .map(Row.from_dict)
               )
        return cls(stm)

    def write_jsonl(self, path):
        '''Write into file in the format of jsonlines

        >>> stb.write_jsonl('person.jsonl') # doctest: +SKIP

        Parameters
        ----------
        path : str or path or file object
            path to the input file

        '''
        if isinstance(path, io.TextIOBase):
            f = path
            self._write_jsonl_file(f)
        else:
            with Path(path).open('wt') as f:
                self._write_jsonl_file(f)

    def _write_jsonl_file(self, f):
        (
            self
            .map(Row.to_dict)
            .map(json.dumps)
            .for_each(lambda line: f.write(line + '\n'))
        )

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

    def show(self, n=10):
        '''print rows

        Parameters
        ----------
        n : int
            number of rows to show
        '''
        try:
            from IPython.display import display
            display_func = display
        except ImportError:
            display_func = print

        showing_obj = _StreamTableShowing(self, n)
        display_func(showing_obj)

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
    def map_fields(self, **field_funcs):
        '''Add or replace fields by applying each row to function

        >>> from carriage import Row, X
        >>> st = StreamTable([Row(x=3, y=4), Row(x=-1, y=2)])
        >>> st.map_fields(z=X.x + X.y).to_list()
        [Row(x=3, y=4, z=7), Row(x=-1, y=2, z=1)]

        Parameters
        ----------
        **field_funcs : Map[field_name, Function]
            Each function will be evaluated with the current row as the only argument, and the return value will be the new value of the field.

        Returns
        -------
        StreamTable
        '''

        return fnt.partial(
            map,
            lambda row:
            row.evolve(**{field: func(row)
                          for field, func in field_funcs.items()}))

    @as_stream
    def select(self, *fields, **field_funcs):
        '''Keep only specified fields, and add/replace fields.

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
    def explode(self, field):
        '''Expand each row into multiple rows for each element in the field

        >>> stb = StreamTable([Row(name='a', nums=[1,3,4]), Row(name='b', nums=[2, 1])])
        >>> stb.explode('nums').show()
        | name   |   nums |
        |--------+--------|
        | a      |      1 |
        | a      |      3 |
        | a      |      4 |
        | b      |      2 |
        | b      |      1 |
        '''
        def _explode_row(row):
            for field_elem in getattr(row, field):
                yield row.evolve(**{field: field_elem})

        def _flatmap_explodes(rows_iter):
            for row in rows_iter:
                yield from _explode_row(row)

        return _flatmap_explodes

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

    def __str__(self):
        return self.tabulate(tablefmt='orgtbl')


class _StreamTableShowing():

    def __init__(self, streamtable, n):
        self.streamtable = streamtable
        self.n = n

    def _repr_html_(self):
        return self.streamtable.tabulate(n=self.n, tablefmt='html')

    def __repr__(self):
        return self.streamtable.tabulate(n=self.n, tablefmt='orgtbl')


StreamTable.tabulate.tablefmts = tabulate_formats
