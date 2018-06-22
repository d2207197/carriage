
import functools as fnt
from .pipeline import Pipeline, Transformer
import operator as op

def transformer_as_underscore(f):
    @fnt.wraps(f)
    def wraped(self, *args, **kwargs):
        trfmr = f(self, *args, **kwargs)
        pipeline = self.pipeline.then(trfmr)
        return type(self)(pipeline=pipeline)

    return wraped
        

class Underscore:
    def __init__(self, *, pipeline=None):
        if pipeline is None:
            pipeline = Pipeline()
        self.pipeline = pipeline


    @transformer_as_underscore
    def __getattr__(self, name):
        return Transformer(f'.{name}', op.attrgetter(name))

    @transformer_as_underscore
    def __getitem__(self, key):
        return Transformer(f'[{key}]', op.itemgetter(key))

    @transformer_as_underscore
    def __eq__(self, other):
        return Transformer(f' == {other}', lambda elem: elem == other)

    @transformer_as_underscore
    def __ne__(self, other):
        return Transformer(f' != {other}', lambda elem: elem != other)

    @transformer_as_underscore
    def __gt__(self, other):
        return Transformer(f' > {other}', lambda elem: elem > other)

    @transformer_as_underscore
    def __ge__(self, other):
        return Transformer(f' >= {other}', lambda elem: elem >= other)

    @transformer_as_underscore
    def __lt__(self, other):
        return Transformer(f' < {other}', lambda elem: elem < other)

    @transformer_as_underscore
    def __le__(self, other):
        return Transformer(f' <= {other}', lambda elem: elem <= other)

    def __call__(self, elem):
        return self.pipeline.transform(elem)

    def __repr__(self):
        return f'<{type(self).__name__} {self.pipeline!r}>'

    def __str__(self):
        return str(self.pipeline)

_ = Underscore()
