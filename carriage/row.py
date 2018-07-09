import itertools as itt

from .repr import short_repr


class Row(tuple):
    '''A named tuple like type without the need of declaring field names
    in advance.

    A Row object can be created anytime when you need it.

    >>> Row(name='Joe', age=30, height=170)
    Row(name='Joe', age=30, height=170)

    >>> Row.from_values([1, 2, 3], fields=['x', 'y', 'z'])
    Row(x=1, y=2, z=3)

    If you are too lazy to name the fields.

    >>> Row.from_values([1, 'a', 9])
    Row(f0=1, f1='a', f2=9)

    You can access field using index or field name in ``O(1)``.

    >>> row = Row(name='Joe', age=30, height=170)
    >>> row.name
    'Joe'
    >>> row[2]
    170

    And it provides some useful method for transforming, converting.
    Because Row is immutable type, all these method create a new Row object.

    >>> row.evolve(height=180)  # I hope so
    Row(name='Joe', age=30, height=180)

    >>> row.evolve(age=row.age + 1)
    Row(name='Joe', age=31, height=170)

    >>> row.to_dict()
    {'name': 'Joe', 'age': 30, 'height': 170}

    >>> row.to_map()
    Map({'name': 'Joe', 'age': 30, 'height': 170})

    Row is iterable. You can unpack it.

    >>> name, age, height = row
    >>> name
    'Joe'
    >>> age
    30

    '''
    @classmethod
    def from_values(cls, values, fields=None):
        '''Create Row from values

        >>> Row.from_values([1, 2, 3])
        Row(f0=1, f1=2, f2=3)
        >>> Row.from_values([1, 2, 3], fields=['x', 'y', 'z'])
        Row(x=1, y=2, z=3)

        '''
        if fields is None:
            return cls(**{f'f{i}': v for i, v in enumerate(values)})
        else:
            return cls(**{f: v for f, v in zip(fields, values)})

    @classmethod
    def from_dict(cls, adict, fields=None):
        '''Create Row from a iterable

        >>> Row.from_dict({'name': 'Joe', 'age': 30})
        Row(name='Joe', age=30)
        '''
        if fields is None:
            return cls(**adict)
        else:
            return cls(**{f: adict[f] for f in fields})

    def __new__(self, **kwargs):
        '''Create Row by field names and values

        >>> Row(name='Joe', age=30, height=170)
        Row(name='Joe', age=30, height=170)

        '''
        row = tuple.__new__(self, kwargs.values())
        row._dict = kwargs

        return row

    def __getnewargs_ex__(self):
        return ((), self._dict)

    def __getattribute__(self, name):
        if name in tuple.__getattribute__(self, '_dict'):
            # Accessing Row fields has higher priority
            # than accessing tuple methods
            return tuple.__getattribute__(self, '_dict')[name]
        else:
            return tuple.__getattribute__(self, name)

    # def __getattr__(self, name):
    #     if name in self._dict:
    #         return self._dict[name]
    #     else:
    #         raise AttributeError(f'{self!r} has no attribute {name!r}')

    def get_opt(self, field):
        '''Get field in Optional type

        >>> from carriage.optional import Some, Nothing
        >>> Row(x=3, y=4).get_opt('x')
        Some(3)
        >>> Row(x=3, y=4).get_opt('z')
        Nothing

        Parameters
        ----------
        field : str
            field name

        Returns
        -------
        Just(value) if field exist
        Nothing if field doesn't exist

        '''
        from .optional import Some, Nothing
        if field in self._dict:
            return Some(getattr(self, field))

        return Nothing

    def get(self, field, fillvalue=None):
        '''Get field

        >>> Row(x=3, y=4).get('x')
        3
        >>> Row(x=3, y=4).get('z', 0)
        0
        '''
        if field in self._dict:
            return getattr(self, field)

        return fillvalue

    def has_field(self, field):
        '''Has field

        >>> Row(x=3, y=4).has_field('x')
        True

        '''
        return field in self._dict

    def __setattr__(self, name, value):
        if name != '_dict':
            raise TypeError("'Row' object does not support item assignment")
        else:
            super().__setattr__(name, value)

    def fields(self):
        return self._dict.keys()

    def evolve(self, **kwargs):
        '''Create a new Row by replacing or adding other fields

        >>> row = Row(x=23, y=9)
        >>> row.evolve(y=12)
        Row(x=23, y=12)
        >>> row.evolve(z=3)
        Row(x=23, y=9, z=3)
        '''
        d = self._dict.copy()
        d.update(kwargs)
        return Row(**d)

    def project(self, *fields):
        '''Create a new Row by keeping only specified fields

        >>> row = Row(x=2, y=3, z=4)
        >>> row.project('x', 'y')
        Row(x=2, y=3)
        '''
        fields = set(fields)
        return Row(**{field: value
                      for field, value in self._dict.items()
                      if field in fields})

    def without(self, *fields):
        '''Create a new Row by removing only specified fields

        >>> row = Row(x=2, y=3, z=4)
        >>> row.without('z')
        Row(x=2, y=3)
        '''
        fields = set(fields)
        return Row(**{field: value
                      for field, value in self._dict.items()
                      if field not in fields})

    def merge(self, *rows):
        '''Create a new merged Row.
        If there's duplicated field name, keep the last value.

        >>> row = Row(x=2, y=3)
        >>> row.merge(Row(y=4, z=5), Row(z=6, u=7))
        Row(x=2, y=4, z=6, u=7)

        '''

        field_value_pairs = itt.chain.from_iterable(row._dict.items()
                                                    for row in (self,) + rows)
        return Row(**{k: v for k, v in field_value_pairs})

    def rename_fields(self, **kwargs):
        '''Create a new Row that field names renamed.

        >>> row = Row(a=2, b=3, c=4)
        >>> row.rename_fields(a='x', b='y')
        Row(x=2, y=3, c=4)

        '''
        return Row(**{kwargs.get(k, k): v for k, v in self._dict.items()})

    def transform(self, **kwargs):
        d = self._dict.copy()
        d.update({k: f(getattr(self, k))for k, f in kwargs.items()})
        return Row(**d)

    def to_dict(self):
        '''Convert to dict'''
        return self._dict.copy()

    def to_map(self):
        '''Convert to Map'''
        from .map import Map
        return Map(**self.to_dict())

    def to_tuple(self):
        '''Convert to tuple'''
        return tuple(self)

    def to_fields(self):
        '''Convert to rows

        >>> Row(x=3, y=4).to_fields()
        [Row(field='x', value=3), Row(field='y', value=4)]
        '''
        return [Row(field=k, value=v) for k, v in self._dict.items()]

    def iter_fields(self):
        '''Convert to rows

        >>> list(Row(x=3, y=4).iter_fields())
        [Row(field='x', value=3), Row(field='y', value=4)]
        '''
        return (Row(field=k, value=v) for k, v in self._dict.items())

    def to_list(self):
        '''Convert to list'''
        return list(self)

    def __repr__(self):
        kwargs_str = ', '.join(
            f'{k}={short_repr.repr(v)}' for k, v in self._dict.items())
        return f'Row({kwargs_str})'


class namedrow:

    def __init__(self, *fields):
        self._fields = fields

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError(
                'Cannot use both args and kwargs to create {type(self)}')

        if args:
            return Row(**{field: value
                          for field, value in zip(self._fields, args)})

        if kwargs:
            return Row(**{field: kwargs[field] for field in self._fields})


CurrPrev = namedrow('curr', 'prev')
CurrNext = namedrow('curr', 'prev')
ValueIndex = namedrow('value', 'index')
KeyValues = namedrow('key', 'values')
KeyValue = namedrow('key', 'value')
