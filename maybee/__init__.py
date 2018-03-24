def maybe(value_or_getter, errors=Exception):
    if callable(value_or_getter):
        return Maybe.except_call(value_or_getter, errors)
    else:
        return Maybe.none(value_or_getter)


class NothingError(ValueError):
    pass


class Maybe():

    @classmethod
    def none(cls, value):
        if value is None:
            return Nothing
        return Just(value)

    @classmethod
    def except_call(cls, getter, errors=Exception):
        try:
            value = getter()
        except errors:
            return Nothing
        else:
            return Just(value)

    def then_maybe(self, action):
        raise NotImplementedError()

    def then(self, action):
        raise NotImplementedError()

    # def or_else(self, other_maybe):
    #     return self.then_maybe(lambda _: other_maybe)

    def get_or(self, else_value):
        raise NotImplementedError()

    def is_just(self):
        raise NotImplementedError()

    def is_nothing(self):
        raise NotImplementedError()


class _Nothing(Maybe):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = Maybe.__new__(cls)

        return cls.__instance

    def get(self):
        raise NothingError('Nothing here')

    def get_or(self, else_value):
        return else_value

    def then_maybe(self, action):
        return Nothing

    def then(self, action):
        return Nothing

    def is_just(self):
        return False

    def is_nothing(self):
        return True

    def __call__(self, *args, **kwargs):
        return Nothing

    def __eq__(self, other):
        if other is Nothing:
            return True

        if other is None:
            return True

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if other is Nothing:
            return False

        if type(other) == Just:
            return True

        return True if other else False

    def __gt__(self, other):
        return False

    def __le__(self, other):
        return True

    def __ge__(self, other):
        if other is Nothing:
            return True

        if other is None:
            return True

        return False

    def __getattr__(self, name):
        return Nothing

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return Nothing

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __repr__(self):
        return 'Nothing'

    def __str__(self):
        return 'Nothing'

    def __nonzero__(self):
        return False


Nothing = _Nothing()


class Just(Maybe):
    def __init__(self, v):
        self.__value = v

    @property
    def v(self):
        return self.__value

    def get(self):
        return self.__value

    def get_or(self, else_value):
        return self.__value

    def then_maybe(self, action):
        value = action(self.__value)
        if isinstance(value, Maybe):
            return value
        else:
            raise TypeError('function should return a Maybe')

    def then(self, action):
        return Just(action(self.__value))

    def is_just(self):
        return True

    def is_nothing(self):
        return False

    def __call__(self, *args, **kwargs):
        return Just(self.__value(*args, **kwargs))

    def __eq__(self, other):
        if other is Nothing:
            return False

        if type(other) == Just:
            return self.get() == other.get()

        raise TypeError(
            f"'==' not supported between instances of 'Just' and {type(other).__name__!r}")

    def __ne__(self, other):
        if other is Nothing:
            return True

        if type(other) == Just:
            return self.get() != other.get()

        raise TypeError(
            f"'!=' not supported between instances of 'Just' and {type(other).__name__!r}")

    def __lt__(self, other):
        if other is Nothing:
            return False

        if type(other) == Just:
            return self.get() < other.get()

        raise TypeError(
            f"'<' not supported between instances of 'Just' and {type(other).__name__!r}")

    def __gt__(self, other):
        if other is Nothing:
            return True

        if type(other) == Just:
            return self.get() > other.get()

        raise TypeError(
            f"'>' not supported between instances of 'Just' and {type(other).__name__!r}")

    def __le__(self, other):
        if other is Nothing:
            return False

        if type(other) == Just:
            return self.get() <= other.get()

        raise TypeError(
            f"'<=' not supported between instances of 'Just' and {type(other).__name__!r}")

    def __ge__(self, other):
        if other is Nothing:
            return True

        if type(other) == Just:
            return self.get() >= other.get()

        raise TypeError(
            f"'>=' not supported between instances of 'Just' and {type(other).__name__!r}")

    def __getattr__(self, name):
        if hasattr(self.__value, name):
            return Just(getattr(self.__value, name))
        else:
            return Nothing

    def __setattr__(self, name, v):
        if name == "_Just__value":
            return super().__setattr__(name, v)

        return setattr(self.__value, name, v)

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, key):
        try:
            return Just(self.__value[key])
        except (KeyError, TypeError, IndexError):
            return Nothing

    def __setitem__(self, key, value):
        self.__value[key] = value

    def __delitem__(self, key):
        del self.__value[key]

    def __iter__(self):
        try:
            iterator = iter(self.__value)
        except TypeError:
            iterator = iter([self.__value])

        return iterator

    def __reversed__(self):
        return maybe(reversed(self.__value))

    def __missing__(self, key):
        klass = self.__value.__class__
        if hasattr(klass, '__missing__') and \
                callable(getattr(klass, '__missing__')):
            return maybe(self.__value.__missing__(key))

        return Nothing

    def __repr__(self):
        return f"Just({self.__value!r})"

    def __str__(self):
        return f"Just({self.__value!s})"

    def __int__(self):
        return int(self.__value)

    def __float__(self):
        return float(self.__value)

    def __complex__(self):
        return complex(self.__value)

    def __oct__(self):
        return oct(self.__value)

    def __hex__(self):
        return hex(self.__value)

    def __index__(self):
        return self.__value.__index__()

    def __trunc__(self):
        return self.__value.__trunc__()

    def __dir__(self):
        return dir(self.__value)

    def __add__(self, other):
        return Just(self.__value + other)

    def __sub__(self, other):
        return Just(self.__value - other)

    def __mul__(self, other):
        return Just(self.__value * other)

    def __floordiv__(self, other):
        return Just(self.__value // other)

    def __div__(self, other):
        return Just(self.__value / other)

    def __mod__(self, other):
        return Just(self.__value % other)

    def __divmod__(self, other):
        return Just(divmod(self.__value, other))

    def __pow__(self, other):
        return Just(self.__value ** other)

    def __lshift__(self, other):
        return Just(self.__value << other)

    def __rshift__(self, other):
        return Just(self.__value >> other)

    def __and__(self, other):
        return Just(self.__value & other)

    def __or__(self, other):
        return Just(self.__value | other)

    def __xor__(self, other):
        return Just(self.__value ^ other)

    def __radd__(self, other):
        return Just(other + self.__value)

    def __rsub__(self, other):
        return Just(other - self.__value)

    def __rmul__(self, other):
        return Just(other * self.__value)

    def __rfloordiv__(self, other):
        return Just(other // self.__value)

    def __rdiv__(self, other):
        return Just(other / self.__value)

    def __rmod__(self, other):
        return Just(other % self.__value)

    def __rdivmod__(self, other):
        return Just(divmod(other, self.__value))

    def __rpow__(self, other):
        return Just(other ** self.__value)

    def __rlshift__(self, other):
        return Just(other << self.__value)

    def __rrshift__(self, other):
        return Just(other >> self.__value)

    def __rand__(self, other):
        return Just(other & self.__value)

    def __ror__(self, other):
        return Just(other | self.__value)

    def __rxor__(self, other):
        return Just(other ^ self.__value)

    def __iadd__(self, other):
        self.__value += other
        return self

    def __isub__(self, other):
        self.__value -= other
        return self

    def __imul__(self, other):
        self.__value *= other
        return self

    def __ifloordiv__(self, other):
        self.__value //= other
        return self

    def __idiv__(self, other):
        self.__value /= other
        return self

    def __imod__(self, other):
        self.__value %= other
        return self

    def __ipow__(self, other):
        self.__value **= other
        return self

    def __ilshift__(self, other):
        self.__value <<= other
        return self

    def __irshift__(self, other):
        self.__value >>= other
        return self

    def __iand__(self, other):
        self.__value &= other
        return self

    def __ior__(self, other):
        self.__value |= other
        return self

    def __ixor__(self, other):
        self.__value ^= other
        return self
