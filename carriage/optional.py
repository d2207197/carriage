import inspect
from abc import abstractmethod, abstractproperty
from functools import wraps

from .monad import Monad


class NothingError(AttributeError):
    pass


class Optional(Monad):
    '''An type for handling special value or exception.

    Create Optional from a function call that may raise exception.

    >>> def divide(a, b):
    ...     return a / b
    >>> Optional.call_exceptable(divide, 2, 4)
    Some(0.5)
    >>> Optional.call_exceptable(divide, 2, 0)
    Nothing

    Create Optional from a value that may be None.

    >>> adict = {'a': 1, 'b': 2, 'c': 3}
    >>> Optional.value_noneable(adict.get('c'))
    Some(3)
    >>> Optional.value_noneable(adict.get('d'))
    Nothing


    Escape from if hell of handling None value or exception. 

    >>> class TreeNode:
    ...     def __init__(self, value, left=None, right=None):
    ...         self.value = value
    ...         self.left = left
    ...         self.right = right

    >>> n = TreeNode(30, TreeNode(5, TreeNode(2)))

    It seem convenient to traversal in tree.
    >>> n.left.left.value
    2

    But both ``left`` and ``right`` might be None. You should take care of
    that.

    >>> result = 0
    >>> if n.left is not None:
    ...     if n.left.left is not None:
    ...         if n.left.left.right is not None:
    ...             if n.left.left.right.left is not None:
    ...                 result = n.left.left.right.left.value * 2
    >>> result
    0


    Now let's replace Noneable value with Optional.

    >>> class TreeNodeOpt:
    ...     def __init__(self, value, left=None, right=None):
    ...         self.value = value
    ...         self.left = Some(left) if left is not None else Nothing
    ...         self.right = Some(left) if left is not None else Nothing

    >>> nopt = TreeNodeOpt(30, TreeNodeOpt(5, TreeNodeOpt(2)))
    >>> (nopt.left
    ...  .bind(lambda n: n.left)
    ...  .map(lambda n: n.value)
    ...  .get_or())
    2

    It seems getting harder to get a value, but actually you are now free from
    having the risk of getting attribute from None. And you don't have to build
    a big, nested if statement for handling it.

    >>> (nopt.left
    ...  .bind(lambda n: n.left)
    ...  .bind(lambda n: n.right)
    ...  .bind(lambda n: n.left)
    ...  .map(lambda n: n.value * 2)
    ...  .get_or(0))
    0

    >>> (nopt.left
    ...  .pluck_attr('left').join()
    ...  .pluck_attr('right').join()
    ...  .pluck_attr('left').join()
    ...  .pluck_attr('value')
    ...  .map(lambda v: v * 2)
    ...  .get_or(0))
    0

    And you can use Optional to handle the original TreeNode.

    >>> n = TreeNode(30, TreeNode(5, TreeNode(2)))
    >>> (Optional.value_noneable(n.left)
    ...  .map(lambda n: n.left).join_noneable()
    ...  .map(lambda n: n.right).join_noneable()
    ...  .map(lambda n: n.left).join_noneable()
    ...  .map(lambda n: n.value * 2)
    ...  .get_or(0))
    0

    It's more elegant to have functions return Optional rather than None or
    other special value.

    >>> def get_right_opt(tn):
    ...     if tn.right is None:
    ...         return Nothing
    ...     return Some(tn.right)

    >>> def get_left_opt(tn):
    ...     if tn.left is None:
    ...         return Nothing
    ...     return Some(tn.left)

    >>> (Optional.value_noneable(n)
    ...  .bind(get_left_opt)
    ...  .bind(get_left_opt)
    ...  .bind(get_right_opt)
    ...  .bind(get_left_opt)
    ...  .map(lambda n: n.value * 2)
    ...  .get_or(0))
    0

    You can create an Optional function with these decorator.


    >>> @Optional.noneable
    ... def get_first(l):
    ...     if len(l) > 0:
    ...         return l[0]
    ...     return None
    >>> get_first([3,4,5])
    Some(3)
    >>> get_first([])
    Nothing

    >>> @Optional.exceptable(IndexError)
    ... def get_first(l):
    ...     return l[0]
    >>> get_first([3,4,5])
    Some(3)
    >>> get_first([])
    Nothing







    '''

    @property
    def _base_type(self):
        return Optional

    @classmethod
    def call_exceptable(cls, getter, *args, errors=Exception, **kwargs):
        try:
            value = getter(*args, **kwargs)
        except errors:
            return Nothing
        else:
            return Some(value)

    ecall = call_exceptable
    expcall = call_exceptable

    @classmethod
    def value_noneable(cls, value):
        if value is None:
            return Nothing
        return Some(value)

    noneval = value_noneable

    @classmethod
    def noneable(cls, f):

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

    @abstractmethod
    def join_noneable(self):
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
    def is_some(self):
        raise NotImplementedError()

    @abstractmethod
    def is_nothing(self):
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

    def flat_map(self, maybe_action):
        return Nothing

    def map(self, action):
        return Nothing

    def then(self, maybe_value):
        return Nothing

    def flatten(self):
        return Nothing

    def join_noneable(self):
        return Nothing

    def ap(self, maybe_value):
        return Nothing

    @property
    def value(self):
        raise NothingError('Nothing here')

    _value_for_cmp = ()

    def get_or(self, else_value=None):
        return else_value

    def get_or_none(self):
        return None

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


NothingCls.__name__ = 'Nothing'


Nothing = NothingCls()


def identity(_): return _


class Some(Optional):
    __slots__ = '_some_value'

    def __init__(self, value):
        self._some_value = value

    def flat_map(self, maybe_action):
        value = maybe_action(self._some_value)
        if isinstance(value, Optional):
            return value
        else:
            raise TypeError('function should return a Optional')

    def map(self, action):
        return Some(action(self._some_value))

    def then(self, maybe_value):
        return maybe_value

    def flatten(self):
        if isinstance(self._some_value, Optional):
            return self._some_value
        else:
            raise TypeError('value should be a Optional')

    def join_noneable(self):
        if self._some_value is None:
            return Nothing
        return self

    def ap(self, maybe_value):
        if maybe_value.is_some():
            return self._some_value(maybe_value.get())
        elif maybe_value.is_nothing():
            return Nothing

    @property
    def value(self):
        return self._some_value

    @property
    def _value_for_cmp(self):
        return (self._some_value,)

    def get_or(self, else_value=None):
        return self._some_value

    def get_or_none(self):
        return self._some_value

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

    def do(self, func):
        '''Call function using this item as parameter.

        '''
        func(self._some_value)


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
