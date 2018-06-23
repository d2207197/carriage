
import functools as fnt
import operator as op

from .pipeline import Pipeline, Transformer
from .repr import repr_args


def lambda_then(f):
    @fnt.wraps(f)
    def wraped(self, *args, **kwargs):
        trfmr = f(self, *args, **kwargs)
        return self._then(trfmr)

    def other_lambda(f):
        @fnt.wraps(f)
        def wraped_(self, *args, **kwargs):
            other = args[0]
            if isinstance(other, Lambda):
                trfmr = f(self, other)
                return X._then(trfmr)
            else:
                return wraped(self, *args, **kwargs)

        return wraped_

    wraped.other_lambda = other_lambda

    return wraped


def Xcall(f):
    '''Elegant partial function builder

    >>> def func(a, b, c=0, d=0):
    ...     return a, b, c, d
    >>> partialfunc = Xcall(func)(X, b=3)
    >>> partialfunc(2)
    (2, 3, 0, 0)
    >>> partialfunc(5)
    (5, 3, 0, 0)
    >>> partialfunc = Xcall(func)(1, 2, c=X.x, d=X.y)
    >>> from carriage import Row
    >>> partialfunc(Row(x=3, y=4))
    (1, 2, 3, 4)
    '''
    @fnt.wraps(f)
    def wraped(*args, **kwargs):
        args_str = repr_args(*args, **kwargs)

        def func(elem):
            actual_args = tuple(arg(elem) if isinstance(arg, Lambda) else arg
                                for arg in args)
            actual_kwargs = {k: arg(elem) if isinstance(arg, Lambda) else arg
                             for k, arg in kwargs.items()}
            return f(*actual_args, **actual_kwargs)

        return X._then(Transformer(f'{f.__name__}({args_str})', func))

    return wraped


class Lambda:
    '''Elegant lambda builder

    - __getitem__: :python:`X['name']`
    - __getattr__: :python:`X.name`
    - comparisons: `X == 5`, `X != 4`, `X > 3`, `X < 2`, ...
    - math operators: `X + 3`, `4 - X`, `pow(X, 2)`, `divmod(3, X)`, ...
    - multiple placeholder: `X + X`, `X.firstname + ' ' + X.lastname`

    >>> from carriage import Row
    >>> d = {'point': Row(x=3, y=4)}
    >>> func = X['point'].x == 3
    >>> func(d)
    True

    .. role:: python(code)
       :language: python

    '''
    __slots__ = '_pipeline',

    def __init__(self, *, pipeline=None):
        if pipeline is None:
            pipeline = Pipeline()
        self._pipeline = pipeline

    @lambda_then
    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError
        return Transformer(f'X.{name}', op.attrgetter(name))

    @lambda_then
    def __getitem__(self, key):
        return Transformer(f'X[{key}]', op.itemgetter(key))

    def _then(self, trfmr):
        return type(self)(pipeline=self._pipeline.then(trfmr))

    @lambda_then
    def __add__(self, other):
        return Transformer(f'X + {other}', lambda elem: elem + other)

    @__add__.other_lambda
    def __add__(self, other):
        return Transformer(f'X + {other}', lambda elem: self(elem) + other(elem))

    @lambda_then
    def __sub__(self, other):
        return Transformer(f'X - {other}', lambda elem: elem - other)

    @__sub__.other_lambda
    def __sub__(self, other):
        return Transformer(f'X - {other}', lambda elem: self(elem) - other(elem))

    @lambda_then
    def __mul__(self, other):
        return Transformer(f'X * {other}', lambda elem: elem * other)

    @__mul__.other_lambda
    def __mul__(self, other):
        return Transformer(f'X * {other}', lambda elem: self(elem) * other(elem))

    @lambda_then
    def __truediv__(self, other):
        return Transformer(f'X / {other}', lambda elem: elem / other)

    @__truediv__.other_lambda
    def __truediv__(self, other):
        return Transformer(f'X / {other}', lambda elem: self(elem) / other(elem))

    @lambda_then
    def __floordiv__(self, other):
        return Transformer(f'X // {other}', lambda elem: elem // other)

    @__floordiv__.other_lambda
    def __floordiv__(self, other):
        return Transformer(f'X // {other}', lambda elem: self(elem) // other(elem))

    @lambda_then
    def __mod__(self, other):
        return Transformer(f'X % {other}', lambda elem: elem % other)

    @__mod__.other_lambda
    def __mod__(self, other):
        return Transformer(f'X % {other}', lambda elem: self(elem) % other(elem))

    @lambda_then
    def __divmod__(self, other):
        return Transformer(f'divmod(X, {other})', lambda elem: divmod(elem, other))

    @__divmod__.other_lambda
    def __divmod__(self, other):
        return Transformer(f'divmod(X % {other})', lambda elem: divmod(self(elem), other(elem)))

    @lambda_then
    def __pow__(self, other):
        return Transformer(f'pow(X % {other})', lambda elem: pow(elem, other))

    @__pow__.other_lambda
    def __pow__(self, other):
        return Transformer(f'pow(X % {other})', lambda elem: pow(self(elem), other(elem)))

    @lambda_then
    def __radd__(self, other):
        return Transformer(f'{other} + X', lambda elem: other + elem)

    @__radd__.other_lambda
    def __radd__(self, other):
        return Transformer(f'{other} + X', lambda elem: other(elem) + self(elem))

    @lambda_then
    def __rsub__(self, other):
        return Transformer(f'{other} - X', lambda elem: other - elem)

    @__rsub__.other_lambda
    def __rsub__(self, other):
        return Transformer(f'{other} - X', lambda elem: other(elem) - self(elem))

    @lambda_then
    def __rmul__(self, other):
        return Transformer(f'{other} * X', lambda elem: other * elem)

    @__rmul__.other_lambda
    def __rmul__(self, other):
        return Transformer(f'{other} * X', lambda elem: other(elem) * self(elem))

    @lambda_then
    def __rtruediv__(self, other):
        return Transformer(f'{other} / X', lambda elem: other / elem)

    @__rtruediv__.other_lambda
    def __rtruediv__(self, other):
        return Transformer(f'{other} / X', lambda elem: other(elem) / self(elem))

    @lambda_then
    def __rfloordiv__(self, other):
        return Transformer(f'{other} // X', lambda elem: other // elem)

    @__rfloordiv__.other_lambda
    def __rfloordiv__(self, other):
        return Transformer(f'{other} // X', lambda elem: other(elem) // self(elem))

    @lambda_then
    def __rmod__(self, other):
        return Transformer(f'{other} % X', lambda elem: other % elem)

    @__rmod__.other_lambda
    def __rmod__(self, other):
        return Transformer(f'{other} % X', lambda elem: other(elem) % self(elem))

    @lambda_then
    def __rdivmod__(self, other):
        return Transformer(f'divmod({other}, X)', lambda elem: divmod(other, elem))

    @__rdivmod__.other_lambda
    def __rdivmod__(self, other):
        return Transformer(f'divmod({other}, X)', lambda elem: divmod(other(elem), self(elem)))

    @lambda_then
    def __rpow__(self, other):
        return Transformer(f'pow({other}, X)', lambda elem: pow(other, elem))

    @__rpow__.other_lambda
    def __rpow__(self, other):
        return Transformer(f'pow({other}, X)', lambda elem: pow(other(elem), self(elem)))

    @lambda_then
    def __eq__(self, other):
        return Transformer(f' == {other}', lambda elem: elem == other)

    @__eq__.other_lambda
    def __eq__(self, other):
        return Transformer(f' == {other}', lambda elem: self(elem) == other(elem))

    @lambda_then
    def __ne__(self, other):
        return Transformer(f' != {other}', lambda elem: elem != other)

    @__ne__.other_lambda
    def __ne__(self, other):
        return Transformer(f' != {other}', lambda elem: self(elem) != other(elem))

    @lambda_then
    def __gt__(self, other):
        return Transformer(f' > {other}', lambda elem: elem > other)

    @__gt__.other_lambda
    def __gt__(self, other):
        return Transformer(f' > {other}', lambda elem: self(elem) > other(elem))

    @lambda_then
    def __ge__(self, other):
        return Transformer(f' >= {other}', lambda elem: elem >= other)

    @__ge__.other_lambda
    def __ge__(self, other):
        return Transformer(f' >= {other}', lambda elem: self(elem) >= other(elem))

    @lambda_then
    def __lt__(self, other):
        return Transformer(f' < {other}', lambda elem: elem < other)

    @__lt__.other_lambda
    def __lt__(self, other):
        return Transformer(f' < {other}', lambda elem: self(elem) < other(elem))

    @lambda_then
    def __le__(self, other):
        return Transformer(f' <= {other}', lambda elem: elem <= other)

    @__le__.other_lambda
    def __le__(self, other):
        return Transformer(f' <= {other}', lambda elem: self(elem) <= other(elem))

    def __call__(self, elem):
        return self._pipeline.transform(elem)

    def __repr__(self):
        return f'<{type(self).__name__} {self._pipeline!r}>'

    def __str__(self):
        return str(self._pipeline)


X = Lambda()
