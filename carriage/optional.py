import inspect
import warnings
from abc import abstractmethod, abstractproperty
from functools import wraps

from .monad import Monad


class NothingAttrError(AttributeError):
    pass


class OkAttrError(AttributeError):
    pass


class ErrAttrError(AttributeError):
    pass


class Optional(Monad):
    '''An type for handling special value or exception.

    Here is a contacts data constructed with multiple levels dictionary.

    >>> contacts = {
    ...     'John Doe': {
    ...         'phone': '0911-222-333',
    ...         'address': {'city': 'hsinchu',
    ...                     'street': '185 Somewhere St.'}},
    ...     'Richard Roe': {
    ...         'phone': '0933-444-555',
    ...         'address': {'city': None,
    ...                     'street': None}},
    ...     'Mark Moe': {
    ...         'address': None},
    ...     'Larry Loe': None
    ... }

    If we need a function to get the formatted city name of some contact,
    we will have a lot of nested `if` statement for handling None or
    other unexpected values.

    >>> def get_city(name):
    ...     contact = contacts.get(name)
    ...     if contact is not None:
    ...         address = contact.get('address')
    ...         if address is not None:
    ...             city = address.get('city')
    ...             if city is not None:
    ...                 return f'City: {city}'
    ...
    ...     return 'No city available'
    >>> get_city('John Doe')
    'City: hsinchu'
    >>> get_city('Richard Roe')
    'No city available'
    >>> get_city('Mark Moe')
    'No city available'
    >>> get_city('Larray Loe')
    'No city available'
    >>> get_city('Not Existing')
    'No city available'

    Optional is useful on handling unexpected return values or exceptions
    and makes the code shorter and more readable.

    >>> def getitem_opt(obj, key):
    ...     """The same as Optional.from_getitem()"""
    ...     try:
    ...         return Some(obj[key])
    ...     except (KeyError, TypeError):
    ...         return Nothing
    ...
    >>> def get_city2(name):
    ...     return (getitem_opt(contacts, name)
    ...             .and_then(lambda contact: getitem_opt(contact, 'address'))
    ...             .and_then(lambda address: getitem_opt(address, 'city'))
    ...             .filter(lambda city: city is not None)
    ...             .map(lambda city: f'City: {city}')
    ...             .get_or('No city available')
    ...             )
    ...
    >>> get_city2('John Doe')
    'City: hsinchu'
    >>> get_city2('Richard Roe')
    'No city available'
    >>> get_city2('Mark Moe')
    'No city available'
    >>> get_city2('Larray Loe')
    'No city available'
    >>> get_city('Not Existing')
    'No city available'

    Create Optional directly

    >>> Some(3)
    Some(3)
    >>> Nothing
    Nothing

    Create Optional by calling a function that may throw exception

    >>> def divide(a, b):
    ...     return a / b
    >>> Optional.from_call(divide, 2, 4, errors=ZeroDivisionError)
    Some(0.5)
    >>> Optional.from_call(divide, 2, 0, errors=ZeroDivisionError)
    Nothing

    Create Optional from a value that may be None or other spectial value.

    >>> adict = {'a': 1, 'b': 2, 'c': 3}
    >>> Optional.from_value(adict.get('c'), nothing_value=None)
    Some(3)
    >>> Optional.from_value(adict.get('d'), nothing_value=None)
    Nothing
    '''

    @property
    def _base_type(self):
        return Optional

    @classmethod
    def from_call(cls, func, *args, errors=(Exception,), **kwargs):
        '''Create an Optional by calling a function

        return Nothing if exception is raised
        '''
        try:
            value = func(*args, **kwargs)
        except errors:
            return Nothing
        else:
            return Some(value)

    @classmethod
    def from_value(cls, value, nothing_value=None):
        '''Create an Optional from a value

        return Nothing if ``value`` equals to ``nothing_value``
        '''
        if value == nothing_value:
            return Nothing
        return Some(value)

    @classmethod
    def noneable(cls, f):
        warnings.warn('Optional.noneable decorator is unnessesary '
                      'and a bad pattern. '
                      'Functions should return Some or Nothing directly '
                      'instead of return None and rely on this decorator.',
                      DeprecationWarning)
        if not callable(f):
            raise TypeError("'f' should be a callable: {f!r}")

        @wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            if res is None:
                return Nothing
            return Some(res)

        return wrapper

    @classmethod
    def exceptable(cls, f_or_error, *more_errors):
        warnings.warn('Optional.exceptable decorator is unnessesary '
                      'and a bad pattern. '
                      'Functions should return Some or Nothing directly '
                      'instead of return None and rely on this decorator.',
                      DeprecationWarning)
        if inspect.isclass(f_or_error) and issubclass(f_or_error, Exception):
            errors = (f_or_error,) + tuple(more_errors)

            def deco(f):
                return cls._wrap_exceptable(f, errors)

            return deco
        if callable(f_or_error):
            f = f_or_error
            errors = Exception
            return cls._wrap_exceptable(f, errors)

    @classmethod
    def _wrap_exceptable(cls, f, errors):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                res = f(*args, **kwargs)
            except errors:
                return Nothing
            else:
                return Some(res)

        return wrapper

    @classmethod
    def unit(cls, value):
        return Some(value)

    @classmethod
    def from_getitem(cls, obj, key):
        '''Create an Optional by calling ``obj[key]``

        return ``Nothing`` if ``KeyError`` or ``TypeError`` is raised
        '''
        try:
            return Some(obj[key])
        except (KeyError, TypeError):
            return Nothing

    @classmethod
    def from_getattr(cls, obj, attr_name):
        '''Create an Optional by calling ``obj.attr_name``

        return Nothing if AttributeError is raised
        '''
        try:
            Some(obj[attr_name])
        except AttributeError:
            return Nothing

    @abstractmethod
    def and_then(self, optional_func):
        '''Return ``optional_func(value)`` if it is Some.
        ``optional_func`` should return Optional

        ``and_then`` is useful for chaining functions that return Optional

        '''
        raise NotImplementedError()

    @abstractmethod
    def map(self, func):
        '''Return ``Some(func(value))`` if it is Some.
        '''
        raise NotImplementedError()

    @abstractmethod
    def join_noneable(self):
        raise NotImplementedError()

    @abstractproperty
    def some(self):
        '''Get the value if it is Some or raise AttributeError if it is not'''
        raise NotImplementedError()

    def value(self):
        return self.some

    @abstractproperty
    def _comparing_value(self):
        raise NotImplementedError()

    @abstractmethod
    def get_or(self, default):
        '''Get the value if it is Some or get `default` if it is Nothing'''
        raise NotImplementedError()

    @abstractmethod
    def get_or_none(self):
        '''Get the value if it is Some or get None if it is Nothing'''
        raise NotImplementedError()

    @abstractmethod
    def filter(self, pred):
        '''Return Nothing if Some doesn't satisfy the predicate'''

    @abstractmethod
    def is_some(self):
        '''Check if it is Some'''
        raise NotImplementedError()

    @abstractmethod
    def is_nothing(self):
        '''Check if it is Nothing'''
        raise NotImplementedError()

    def pluck(self, key):
        return self.map(lambda d: d[key])

    def pluck_opt(self, key):
        return self.flat_map(lambda d: Some(d[key])
                             if key in d else Nothing)

    def pluck_attr(self, attr):
        return self.map(lambda obj: getattr(obj, attr))


class NothingCls(Optional):
    __slots__ = ()
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def and_then(self, optional_func):
        return Nothing

    flat_map = and_then

    def map(self, func):
        return Nothing

    def then(self, optional_value):
        return Nothing

    def flatten(self):
        return Nothing

    def join_noneable(self):
        return Nothing

    def ap(self, optional_value):
        return Nothing

    @property
    def some(self):
        raise NothingAttrError(
            '`some` attribute does not exist in Nothing instance')

    @property
    def value(self):
        raise NothingAttrError(
            '`value` attribute does not exist in Nothing instance')

    _comparing_value = ()

    def get_or(self, else_value=None):
        return else_value

    def get_or_none(self):
        return None

    def filter(self, pred):
        return Nothing

    def is_some(self):
        return False

    def is_nothing(self):
        return True

    def __len__(self):
        return 0

    def __iter__(self):
        return

    def __repr__(self):
        return 'Nothing'

    def __str__(self):
        return 'Nothing'

    def to_result(self, err_value):
        return Err(self._err_value)


NothingCls.__name__ = 'Nothing'


Nothing = NothingCls()


def identity(_): return _


class Some(Optional):
    __slots__ = '_some_value'

    def __init__(self, value):
        self._some_value = value

    def map(self, func):
        return Some(func(self._some_value))

    def and_then(self, optional_func):
        value = optional_func(self._some_value)
        if isinstance(value, Optional):
            return value
        else:
            raise TypeError('function should return a Optional')

    flat_map = and_then

    def then(self, optional_value):
        return optional_value

    def flatten(self):
        if isinstance(self._some_value, Optional):
            return self._some_value
        else:
            raise TypeError('value should be a Optional')

    def join_noneable(self):
        if self._some_value is None:
            return Nothing
        return self

    def ap(self, optional_value):
        if optional_value.is_some():
            return self._some_value(optional_value.get())
        elif optional_value.is_nothing():
            return Nothing

    @property
    def some(self):
        return self._some_value

    @property
    def value(self):
        return self._some_value

    @property
    def _comparing_value(self):
        return (self._some_value,)

    def get_or(self, else_value=None):
        return self._some_value

    def get_or_none(self):
        return self._some_value

    def filter(self, pred):
        if pred(self._some_value):
            return self
        else:
            return Nothing

    def is_some(self):
        return True

    def is_nothing(self):
        return False

    def __len__(self):
        raise 1

    def __iter__(self):
        yield self._some_value

    def __repr__(self):
        return f'Some({self._some_value!r})'

    def __str__(self):
        return f'Some({self._some_value!s})'

    def to_result(self, err_value):
        return Ok(self._some_value)

    def do(self, func):
        '''Call function using this item as parameter.

        '''
        func(self._some_value)


class Result(Monad):

    @property
    def _base_type(self):
        return Optional

    @classmethod
    def unit(cls, value):
        return Ok(value)

    @classmethod
    def from_optional(cls, opt, err_value):
        if isinstance(opt, Some):
            return Ok(opt.value)
        elif opt is Nothing:
            return Err(err_value)
        else:
            raise ValueError('opt should be in Optional type')

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        raise NotImplementedError()

    @abstractmethod
    def ok_opt(self):
        raise NotImplementedError()

    @abstractmethod
    def err_opt(self):
        raise NotImplementedError()

    @abstractmethod
    def ok(self):
        raise NotImplementedError()

    @abstractmethod
    def err(self):
        raise NotImplementedError()

    @abstractmethod
    def and_then(self, ok_result_func):
        raise NotImplementedError()

    @abstractmethod
    def or_else(self, err_result_func):
        raise NotImplementedError()

    @abstractmethod
    def get_or(self, default):
        raise NotImplementedError()

    @abstractmethod
    def get_or_none(self):
        raise NotImplementedError()

    @abstractmethod
    def map(self, func):
        raise NotImplementedError()

    @abstractmethod
    def map_error(self, func):
        raise NotImplementedError()

    @abstractmethod
    def to_optional(self):
        raise NotImplementedError()

    @abstractmethod
    def is_ok(self):
        raise NotImplementedError()

    @abstractmethod
    def is_err(self):
        raise NotImplementedError()


class Ok(Result):
    __slots__ = '_ok_value'

    def __init__(self, ok_value):
        self._ok_value = ok_value

    @property
    def _comparing_value(self):
        return (self._ok_value,)

    def __iter__(self):
        yield self._ok_value

    def __len__(self):
        return 1

    def __repr__(self):
        return f'Ok({self._ok_value})'

    def ok_opt(self):
        return Some(self._ok_value)

    def err_opt(self):
        return Nothing

    @property
    def ok(self):
        return self._ok_value

    value = ok

    @property
    def err(self):
        raise OkAttrError(
            'err attribute does not exist in Ok object')

    def and_then(self, result_func):
        result = result_func(self._ok_value)
        if not isinstance(result, Result):
            raise ValueError('function should return Result object')
        return result

    def or_else(self, result_func):
        return self

    def get_or(self, default):
        return self._ok_value

    def get_or_none(self):
        return self._ok_value

    def get_err_or(self, default):
        return default

    def map(self, func):
        return Ok(func(self._ok_value))

    def map_error(self, func):
        return self

    def to_optional(self):
        return Some(self._ok_value)

    def is_ok(self):
        return True

    def is_err(self):
        return False


class Err(Result):
    __slots__ = '_err_value'

    def __init__(self, err_value):
        self._err_value = err_value

    def __iter__(self):
        return

    def __len__(self):
        return 0

    def __repr__(self):
        return f'Err({self._err_value})'

    def ok_opt(self):
        return Nothing

    def err_opt(self):
        return Some(self._err_value)

    @property
    def ok(self):
        raise OkAttrError('ok attribute does not exist in Err object')

    @property
    def err(self):
        return self._err_value

    def and_then(self, ok_result_func):
        return self

    def or_else(self, err_result_func):
        result = err_result_func(self._err_value)
        if not isinstance(result, Result):
            raise ValueError('function should return Result object')
        return result

    def get_or(self, default):
        return default

    def get_or_none(self):
        return None

    def map(self, func):
        return self

    def map_error(self, func):
        return Err(func(self._err_value))

    def to_optional(self):
        return Nothing

    def is_ok(self):
        return False

    def is_err(self):
        return True


class SomeOp(Some):

    def __call__(self, *args, **kwargs):
        return Some(self._some_value(*args, **kwargs))

    def __getattr__(self, name):
        if hasattr(self._some_value, name):
            return Some(getattr(self._some_value, name))
        else:
            return Nothing

    def __setattr__(self, name, v):
        if name == f"_some_value":
            return super().__setattr__(name, v)

        return setattr(self._some_value, name, v)

    def __getitem__(self, key):
        return Some(self._some_value[key])

    def __setitem__(self, key, value):
        self._some_value[key] = value

    def __delitem__(self, key):
        del self._some_value[key]

    def __len__(self):
        return len(self._some_value)

    def __iter__(self):
        return iter(self._some_value)

    def __reversed__(self):
        return Some(reversed(self._some_value))

    # def __missing__(self, key):
        # klass = self._some_value.__class__
        # if hasattr(klass, '__missing__') and \
        #         callable(getattr(klass, '__missing__')):
        #     return Some(self._some_value.__missing__(key))

        # return Nothing

    def __repr__(self):
        return f"{type(self).__name__}({self._some_value!r})"

    def __str__(self):
        return f"{type(self).__name__}({self._some_value!s})"

    def __int__(self):
        return int(self._some_value)

    def __float__(self):
        return float(self._some_value)

    def __complex__(self):
        return complex(self._some_value)

    def __oct__(self):
        return oct(self._some_value)

    def __hex__(self):
        return hex(self._some_value)

    def __index__(self):
        return self._some_value.__index__()

    def __trunc__(self):
        return self._some_value.__trunc__()

    def __dir__(self):
        return dir(self._some_value)

    def __add__(self, other):
        return Some(self._some_value + other)

    def __sub__(self, other):
        return Some(self._some_value - other)

    def __mul__(self, other):
        return Some(self._some_value * other)

    def __floordiv__(self, other):
        return Some(self._some_value // other)

    def __div__(self, other):
        return Some(self._some_value / other)

    def __mod__(self, other):
        return Some(self._some_value % other)

    def __divmod__(self, other):
        return Some(divmod(self._some_value, other))

    def __pow__(self, other):
        return Some(self._some_value ** other)

    def __lshift__(self, other):
        return Some(self._some_value << other)

    def __rshift__(self, other):
        return Some(self._some_value >> other)

    def __and__(self, other):
        return Some(self._some_value & other)

    def __or__(self, other):
        return Some(self._some_value | other)

    def __xor__(self, other):
        return Some(self._some_value ^ other)

    def __radd__(self, other):
        return Some(other + self._some_value)

    def __rsub__(self, other):
        return Some(other - self._some_value)

    def __rmul__(self, other):
        return Some(other * self._some_value)

    def __rfloordiv__(self, other):
        return Some(other // self._some_value)

    def __rdiv__(self, other):
        return Some(other / self._some_value)

    def __rmod__(self, other):
        return Some(other % self._some_value)

    def __rdivmod__(self, other):
        return Some(divmod(other, self._some_value))

    def __rpow__(self, other):
        return Some(other ** self._some_value)

    def __rlshift__(self, other):
        return Some(other << self._some_value)

    def __rrshift__(self, other):
        return Some(other >> self._some_value)

    def __rand__(self, other):
        return Some(other & self._some_value)

    def __ror__(self, other):
        return Some(other | self._some_value)

    def __rxor__(self, other):
        return Some(other ^ self._some_value)

    def __iadd__(self, other):
        self._some_value += other
        return self

    def __isub__(self, other):
        self._some_value -= other
        return self

    def __imul__(self, other):
        self._some_value *= other
        return self

    def __ifloordiv__(self, other):
        self._some_value //= other
        return self

    def __idiv__(self, other):
        self._some_value /= other
        return self

    def __imod__(self, other):
        self._some_value %= other
        return self

    def __ipow__(self, other):
        self._some_value **= other
        return self

    def __ilshift__(self, other):
        self._some_value <<= other
        return self

    def __irshift__(self, other):
        self._some_value >>= other
        return self

    def __iand__(self, other):
        self._some_value &= other
        return self

    def __ior__(self, other):
        self._some_value |= other
        return self

    def __ixor__(self, other):
        self._some_value ^= other
        return self


class SomeOptionalNone(Some):
    def __init__(self, value):
        self._some_value = value

    def __call__(self, *args, **kwargs):
        return Optional(self._some_value(*args, **kwargs))

    def __getattr__(self, name):
        attr = getattr(self._some_value, name)
        if callable(attr):
            return SomeOptionalNone(attr)
        return Optional(attr)

    def __getitem__(self, key):
        return Optional(self._some_value[key])

    def __reversed__(self):
        return Optional(reversed(self._some_value))

    def __missing__(self, key):
        # TODO: review
        klass = self._some_value.__class__
        if (hasattr(klass, '__missing__') and
                callable(getattr(klass, '__missing__'))):
            return Optional(self._some_value.__missing__(key))

        return Nothing

    def __add__(self, other):
        return Optional(self._some_value + other)

    def __sub__(self, other):
        return Optional(self._some_value - other)

    def __mul__(self, other):
        return Optional(self._some_value * other)

    def __floordiv__(self, other):
        return Optional(self._some_value // other)

    def __div__(self, other):
        return Optional(self._some_value / other)

    def __mod__(self, other):
        return Optional(self._some_value % other)

    def __divmod__(self, other):
        return Optional(divmod(self._some_value, other))

    def __pow__(self, other):
        return Optional(self._some_value ** other)

    def __lshift__(self, other):
        return Optional(self._some_value << other)

    def __rshift__(self, other):
        return Optional(self._some_value >> other)

    def __and__(self, other):
        return Optional(self._some_value & other)

    def __or__(self, other):
        return Optional(self._some_value | other)

    def __xor__(self, other):
        return Optional(self._some_value ^ other)

    def __radd__(self, other):
        return Optional(other + self._some_value)

    def __rsub__(self, other):
        return Optional(other - self._some_value)

    def __rmul__(self, other):
        return Optional(other * self._some_value)

    def __rfloordiv__(self, other):
        return Optional(other // self._some_value)

    def __rdiv__(self, other):
        return Optional(other / self._some_value)

    def __rmod__(self, other):
        return Optional(other % self._some_value)

    def __rdivmod__(self, other):
        return Optional(divmod(other, self._some_value))

    def __rpow__(self, other):
        return Optional(other ** self._some_value)

    def __rlshift__(self, other):
        return Optional(other << self._some_value)

    def __rrshift__(self, other):
        return Optional(other >> self._some_value)

    def __rand__(self, other):
        return Optional(other & self._some_value)

    def __ror__(self, other):
        return Optional(other | self._some_value)

    def __rxor__(self, other):
        return Optional(other ^ self._some_value)
