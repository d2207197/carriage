
class Transformer:
    __slots__ = '_name', '_func'

    def __init__(self, name, func):
        self._name = name
        self._func = func

    def transform(self, data):
        return self._func(data)

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f'<{type(self).__name__} {self._name}>'



class Pipeline:
    __slots__ = '_transformers',

    def __init__(self, transformers=None):
        if transformers is None:
            transformers = []

        self._transformers = transformers

    def transform(self, data):
        for transformer in self._transformers:
            data = transformer.transform(data)
        return data

    @property
    def transformers(self):
        return self._transformers


    def then(self, transformer):
        return type(self)(self._transformers + [transformer])

    def extended(self, other):
        return type(self)(self._transformers + other._transformers)

    def __repr__(self):
        return f'<{type(self).__name__} {self._transformers!r}>'

    def is_empty(self):
        return len(self._transformers) == 0

    def __len__(self):
        return len(self._transformers)

    def __str__(self):
        return (
            # f'{type(self).__name__}\n -> ' +
            '\n'.join(f' -> {trfmr.name}' for trfmr in self._transformers)
        )
