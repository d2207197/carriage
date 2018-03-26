from abc import ABC, abstractmethod, abstractproperty
from functools import wraps


class NothingError(AttributeError):
    pass


class Optional(ABC):

    @classmethod
    def call_exceptable(cls, getter, *args, errors=Exception, **kwargs):
        try:
            value = getter(*args, **kwargs)
        except errors:
            return Nothing_inst
        else:
            return Some(value)

    ecall = call_exceptable

    @classmethod
    def value_noneable(cls, value):
        if value is None:
            return Nothing_inst
        return Some(value)

    nval = value_noneable

    @classmethod
    def noneable(cls, f):

        if not callable(f):
            raise TypeError("'f' should be a callable: {f!r}")

        @wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            if res is None:
                return Nothing_inst
            return Some(res)

        return wrapper

    @classmethod
    def exceptable(cls, f_or_errors):
        if callable(f_or_errors):
            f = f_or_errors
            errors = Exception
            return cls._wrap_exceptable(f, errors)
        else:
            errors = f_or_errors

            def deco(f):
                return cls._wrap_exceptable(f, errors)
            return deco

    @classmethod
    def _wrap_exceptable(cls, f, errors):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                res = f(*args, **kwargs)
            except errors:
                return Nothing_inst
            else:
                return Some(res)

        return wrapper

    @abstractmethod
    def bind(self, maybe_action):
        raise NotImplementedError()

    @abstractmethod
    def map(self, action):
        raise NotImplementedError()

    @abstractmethod
    def then(self, maybe_value):
        raise NotImplementedError()

    @abstractmethod
    def join(self):
        raise NotImplementedError()

    @abstractmethod
    def ap(self, maybe_value):
        raise NotImplementedError()

    @abstractproperty
    def value(self):
        raise NotImplementedError()

    @abstractproperty
    def _value_for_cmp(self):
        raise NotImplementedError()

    @abstractmethod
    def get_or(self, default):
        raise NotImplementedError()

    @abstractmethod
    def get_or_none(self):
        raise NotImplementedError()

    @abstractmethod
    def is_just(self):
        raise NotImplementedError()

    @abstractmethod
    def is_nothing(self):
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, Optional):
            return self._value_for_cmp == other._value_for_cmp

        raise TypeError(
            "'==' not supported between instances of "
            f"'Optional' and {type(other).__name__!r}")

    def __ne__(self, other):
        if isinstance(other, Optional):
            return self._value_for_cmp != other._value_for_cmp

        raise TypeError(
            "'!=' not supported between instances of "
            f"'Optional' and {type(other).__name__!r}")

    def __gt__(self, other):
        if isinstance(other, Optional):
            return self._value_for_cmp > other._value_for_cmp

        raise TypeError(
            "'>' not supported between instances of "
            f"'Optional' and {type(other).__name__!r}")

    def __lt__(self, other):
        if isinstance(other, Optional):
            return self._value_for_cmp < other._value_for_cmp

        raise TypeError(
            "'<' not supported between instances of "
            f"'Optional' and {type(other).__name__!r}")

    def __ge__(self, other):
        if isinstance(other, Optional):
            return self._value_for_cmp >= other._value_for_cmp

        raise TypeError(
            "'>=' not supported between instances of "
            f"'Optional' and {type(other).__name__!r}")

    def __le__(self, other):
        if isinstance(other, Optional):
            return self._value_for_cmp <= other._value_for_cmp

        raise TypeError(
            "'<=' not supported between instances of "
            f"'Optional' and {type(other).__name__!r}")


class Nothing(Optional):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def bind(self, maybe_action):
        return Nothing_inst

    def map(self, action):
        return Nothing_inst

    def then(self, maybe_value):
        return Nothing_inst

    def join(self):
        return Nothing_inst

    def ap(self, maybe_value):
        return Nothing_inst

    @property
    def value(self):
        raise NothingError('Nothing here')

    _value_for_cmp = ()

    def get_or(self, else_value=None):
        return else_value

    def get_or_none(self):
        return None

    def is_just(self):
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


Nothing_inst = Nothing()


def identity(_): return _


class Some(Optional):

    def __init__(self, value):
        self._just_value = value

    def bind(self, maybe_action):
        value = maybe_action(self._just_value)
        if isinstance(value, Optional):
            return value
        else:
            raise TypeError('function should return a Optional')

    def map(self, action):
        return Some(action(self._just_value))

    def then(self, maybe_value):
        return maybe_value

    def join(self):
        if isinstance(self._just_value, Optional):
            return self._just_value
        else:
            raise TypeError('value should be a Optional')

    def ap(self, maybe_value):
        if maybe_value.is_just():
            return self._just_value(maybe_value.get())
        elif maybe_value.is_nothing():
            return Nothing_inst

    @property
    def value(self):
        return self._just_value

    @property
    def _value_for_cmp(self):
        return (self._just_value,)

    def get_or(self, else_value=None):
        return self._just_value

    def get_or_none(self):
        return self._just_value

    def is_just(self):
        return True

    def is_nothing(self):
        return False

    def __len__(self):
        raise 1

    def __iter__(self):
        yield self._just_value

    def __repr__(self):
        return f'Some({self._just_value!r})'

    def __str__(self):
        return f'Some({self._just_value!s})'


class SomeOp(Some):

    def __call__(self, *args, **kwargs):
        return Some(self._just_value(*args, **kwargs))

    def __getattr__(self, name):
        if hasattr(self._just_value, name):
            return Some(getattr(self._just_value, name))
        else:
            return Nothing_inst

    def __setattr__(self, name, v):
        # if name == f"_just_value":
        #     return super().__setattr__(name, v)

        return setattr(self._just_value, name, v)

    def __getitem__(self, key):
        return Some(self._just_value[key])

    def __setitem__(self, key, value):
        self._just_value[key] = value

    def __delitem__(self, key):
        del self._just_value[key]

    def __len__(self):
        return len(self._just_value)

    def __iter__(self):
        return iter(self._just_value)

    def __reversed__(self):
        return Some(reversed(self._just_value))

    # def __missing__(self, key):
        # klass = self._just_value.__class__
        # if hasattr(klass, '__missing__') and \
        #         callable(getattr(klass, '__missing__')):
        #     return Some(self._just_value.__missing__(key))

        # return Nothing_inst

    def __repr__(self):
        return f"{type(self).__name__}({self._just_value!r})"

    def __str__(self):
        return f"{type(self).__name__}({self._just_value!s})"

    def __int__(self):
        return int(self._just_value)

    def __float__(self):
        return float(self._just_value)

    def __complex__(self):
        return complex(self._just_value)

    def __oct__(self):
        return oct(self._just_value)

    def __hex__(self):
        return hex(self._just_value)

    def __index__(self):
        return self._just_value.__index__()

    def __trunc__(self):
        return self._just_value.__trunc__()

    def __dir__(self):
        return dir(self._just_value)

    def __add__(self, other):
        return Some(self._just_value + other)

    def __sub__(self, other):
        return Some(self._just_value - other)

    def __mul__(self, other):
        return Some(self._just_value * other)

    def __floordiv__(self, other):
        return Some(self._just_value // other)

    def __div__(self, other):
        return Some(self._just_value / other)

    def __mod__(self, other):
        return Some(self._just_value % other)

    def __divmod__(self, other):
        return Some(divmod(self._just_value, other))

    def __pow__(self, other):
        return Some(self._just_value ** other)

    def __lshift__(self, other):
        return Some(self._just_value << other)

    def __rshift__(self, other):
        return Some(self._just_value >> other)

    def __and__(self, other):
        return Some(self._just_value & other)

    def __or__(self, other):
        return Some(self._just_value | other)

    def __xor__(self, other):
        return Some(self._just_value ^ other)

    def __radd__(self, other):
        return Some(other + self._just_value)

    def __rsub__(self, other):
        return Some(other - self._just_value)

    def __rmul__(self, other):
        return Some(other * self._just_value)

    def __rfloordiv__(self, other):
        return Some(other // self._just_value)

    def __rdiv__(self, other):
        return Some(other / self._just_value)

    def __rmod__(self, other):
        return Some(other % self._just_value)

    def __rdivmod__(self, other):
        return Some(divmod(other, self._just_value))

    def __rpow__(self, other):
        return Some(other ** self._just_value)

    def __rlshift__(self, other):
        return Some(other << self._just_value)

    def __rrshift__(self, other):
        return Some(other >> self._just_value)

    def __rand__(self, other):
        return Some(other & self._just_value)

    def __ror__(self, other):
        return Some(other | self._just_value)

    def __rxor__(self, other):
        return Some(other ^ self._just_value)

    def __iadd__(self, other):
        self._just_value += other
        return self

    def __isub__(self, other):
        self._just_value -= other
        return self

    def __imul__(self, other):
        self._just_value *= other
        return self

    def __ifloordiv__(self, other):
        self._just_value //= other
        return self

    def __idiv__(self, other):
        self._just_value /= other
        return self

    def __imod__(self, other):
        self._just_value %= other
        return self

    def __ipow__(self, other):
        self._just_value **= other
        return self

    def __ilshift__(self, other):
        self._just_value <<= other
        return self

    def __irshift__(self, other):
        self._just_value >>= other
        return self

    def __iand__(self, other):
        self._just_value &= other
        return self

    def __ior__(self, other):
        self._just_value |= other
        return self

    def __ixor__(self, other):
        self._just_value ^= other
        return self


class SomeOptionalNone(Some):
    def __init__(self, value):
        self._just_value = value

    def __call__(self, *args, **kwargs):
        return Optional(self._just_value(*args, **kwargs))

    def __getattr__(self, name):
        attr = getattr(self._just_value, name)
        if callable(attr):
            return SomeOptionalNone(attr)
        return Optional(attr)

    def __getitem__(self, key):
        return Optional(self._just_value[key])

    def __reversed__(self):
        return Optional(reversed(self._just_value))

    def __missing__(self, key):
        # TODO: review
        klass = self._just_value.__class__
        if (hasattr(klass, '__missing__') and
                callable(getattr(klass, '__missing__'))):
            return Optional(self._just_value.__missing__(key))

        return Nothing_inst

    def __add__(self, other):
        return Optional(self._just_value + other)

    def __sub__(self, other):
        return Optional(self._just_value - other)

    def __mul__(self, other):
        return Optional(self._just_value * other)

    def __floordiv__(self, other):
        return Optional(self._just_value // other)

    def __div__(self, other):
        return Optional(self._just_value / other)

    def __mod__(self, other):
        return Optional(self._just_value % other)

    def __divmod__(self, other):
        return Optional(divmod(self._just_value, other))

    def __pow__(self, other):
        return Optional(self._just_value ** other)

    def __lshift__(self, other):
        return Optional(self._just_value << other)

    def __rshift__(self, other):
        return Optional(self._just_value >> other)

    def __and__(self, other):
        return Optional(self._just_value & other)

    def __or__(self, other):
        return Optional(self._just_value | other)

    def __xor__(self, other):
        return Optional(self._just_value ^ other)

    def __radd__(self, other):
        return Optional(other + self._just_value)

    def __rsub__(self, other):
        return Optional(other - self._just_value)

    def __rmul__(self, other):
        return Optional(other * self._just_value)

    def __rfloordiv__(self, other):
        return Optional(other // self._just_value)

    def __rdiv__(self, other):
        return Optional(other / self._just_value)

    def __rmod__(self, other):
        return Optional(other % self._just_value)

    def __rdivmod__(self, other):
        return Optional(divmod(other, self._just_value))

    def __rpow__(self, other):
        return Optional(other ** self._just_value)

    def __rlshift__(self, other):
        return Optional(other << self._just_value)

    def __rrshift__(self, other):
        return Optional(other >> self._just_value)

    def __rand__(self, other):
        return Optional(other & self._just_value)

    def __ror__(self, other):
        return Optional(other | self._just_value)

    def __rxor__(self, other):
        return Optional(other ^ self._just_value)
