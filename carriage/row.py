

class Row(tuple):
    '''A named tuple like type without the need of declaring field names.

    A Row object can be created anytime when you need it.

    >>> Row(name='Joe', age=30, height=170)
    Row(name='Joe', age=30, height=170)

    If you are too lazy to name the fields.

    >>> Row.from_values(1, 'a', 9)
    Row(v0=1, v1='a', v2=9)
    >>> Row.from_iterable(range(3))
    Row(v0=0, v1=1, v2=2)

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

    >>> row.asdict()
    {'name': 'Joe', 'age': 30, 'height': 170}

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
    def from_values(cls, *args):
        return cls.from_iterable(args)

    @classmethod
    def from_iterable(cls, iterable):
        return cls(**{f'v{i}': v for i, v in enumerate(iterable)})

    def __new__(self, **kwargs):
        row = tuple.__new__(self, kwargs.values())
        row._dict = kwargs

        return row

    def __getattribute__(self, name):
        if name in tuple.__getattribute__(self, '_dict'):
            # Accessing Row fields has higher priority
            # than accessing tuple methods
            return tuple.__getattribute__(self, '_dict')[name]
        else:
            return tuple.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name != '_dict':
            raise TypeError("'Row' object does not support item assignment")
        else:
            super().__setattr__(name, value)

    # def __getattr__(self, name):
    #     if name in self._dict:
    #         return self._dict[name]
    #     else:
    #         raise AttributeError(f'{self!r} has no attribute {name!r}')

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

    to_dict = asdict

    def to_map(self):
        from .map import Map
        return Map(self.asdict())

    def to_tuple(self):
        return tuple(self)

    def to_list(self):
        return list(self)

    def __repr__(self):
        kwargs_str = ', '.join(f'{k}={v!r}' for k, v in self._dict.items())
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
