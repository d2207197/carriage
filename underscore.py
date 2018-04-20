import functools as fnt


def op(f):
    def op_(self, other):

        def f_(elem):
            return f(elem, other)

        return f_


class Underscore:

    def apply(self, func, *args, **kwargs):
        '''apply function

        >>> def times_2(n): return n * 2
        >>> f = _.apply(times_2)
        >>> f(3)
        6

        >>> def multiply(n, m): return n * m
        >>> f = _.apply(multiply, n=3)
        >>> f(m=4)
        12

        >>> def multiply(n, m): return n * m
        >>> f = _.apply(multiply, m=3)
        >>> f(4)
        12

        '''
        return fnt.partial(func, *args, **kwargs)

    # def __call__(self, *args, **kwargs):
    #     return Some(self._some_value(*args, **kwargs))

    def __getattr__(self, name):
        '''getattr

        >>> f = _.x
        >>> class Point:
        ...     x=1
        ...     y=2
        >>> f(Point)
        1

        '''
        def getattr_(elem):
            return getattr(elem, name)

        return getattr_

    # def __setattr__(self, name, v):
    #     if name == f"_some_value":
    #         return super().__setattr__(name, v)

    #     return setattr(self._some_value, name, v)

    def __getitem__(self, key):
        '''getitem

        >>> f = _['y']
        >>> d = {'x': 1, 'y': 2}
        >>> f(d)
        2

        '''
        def getitem_(elem):
            return elem[key]

        return getitem_

    # def __setitem__(self, key, value):
    #     self._some_value[key] = value

    # def __delitem__(self, key):
    #     del self._some_value[key]

    # def __len__(self):
    #     '''len

    #     >>> l = [1, 2, 3]
    #     >>> f = len(_)
    #     >>> f(l)
    #     '''
    #     def len_(elem):
    #         return len(elem)
    #     return len_

    # def __iter__(self):
    #     return iter(self._some_value)

    # def __reversed__(self):
    #     return Some(reversed(self._some_value))

    # def __missing__(self, key):
        # klass = self._some_value.__class__
        # if hasattr(klass, '__missing__') and \
        #         callable(getattr(klass, '__missing__')):
        #     return Some(self._some_value.__missing__(key))

        # return Nothing

    # def __repr__(self):
    #     return f"{type(self).__name__}({self._some_value!r})"

    # def __str__(self):
    #     return f"{type(self).__name__}({self._some_value!s})"

    # def __int__(self):
    #     return int(self._some_value)

    # def __float__(self):
    #     return float(self._some_value)

    # def __complex__(self):
    #     return complex(self._some_value)

    # def __oct__(self):
    #     return oct(self._some_value)

    # def __hex__(self):
    #     return hex(self._some_value)

    # def __index__(self):
    #     return self._some_value.__index__()

    # def __trunc__(self):
    #     return self._some_value.__trunc__()

    # def __dir__(self):
    #     return dir(self._some_value)

    def __add__(self, other):
        '''add

        >>> f = _ + 3
        >>> f(30)
        33

        '''
        def add_(elem):
            return elem + other
        return add_

    def __sub__(self, other):
        '''sub

        >>> f = _ - 3
        >>> f(30)
        27

        '''
        def sub_(elem):
            return elem - other
        return sub_

    def __mul__(self, other):
        '''mul

        >>> f = _ * 3
        >>> f(5)
        15

        '''

        def mul_(elem):
            return elem * other

        return mul_

    def __floordiv__(self, other):
        '''floordiv

        >>> f = _ // 3
        >>> f(13)
        4

        '''

        def floordiv_(elem):
            return elem // other

        return floordiv_

    def __div__(self, other):
        '''div

        # >>> f = _ / 3
        # >>> f(13)
        # 4.3333

        '''

        def div_(elem):
            return elem / other

        return div_

    def __mod__(self, other):
        '''div

        >>> f = _ % 3
        >>> f(13)
        1

        '''

        def div_(elem):
            return elem % other

        return div_

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


_ = Underscore()
