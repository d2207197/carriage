from abc import ABC, abstractmethod, abstractproperty


class Monad(ABC):

    @abstractmethod
    def unit(self, value):
        raise NotImplementedError()

    @abstractmethod
    def flat_map(self, monad_action):
        raise NotImplementedError()

    def bind(self, monad_action):
        raise self.flat_map()

    @abstractmethod
    def map(self, action):
        raise NotImplementedError()

    def fmap(self, action):
        return self.map(action)

    @abstractmethod
    def flatten(self):
        raise NotImplementedError()

    def join(self):
        return self.flatten()

    @abstractmethod
    def then(self, maybe_value):
        raise NotImplementedError()

    @abstractmethod
    def ap(self, maybe_value):
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

    @abstractproperty
    def _base_type(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, self._base_type):
            return self._value_for_cmp == other._value_for_cmp

        raise TypeError(
            "'==' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __ne__(self, other):
        if isinstance(other, self._base_type):
            return self._value_for_cmp != other._value_for_cmp

        raise TypeError(
            "'!=' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __gt__(self, other):
        if isinstance(other, self._base_type):
            return self._value_for_cmp > other._value_for_cmp

        raise TypeError(
            "'>' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __lt__(self, other):
        if isinstance(other, self._base_type):
            return self._value_for_cmp < other._value_for_cmp

        raise TypeError(
            "'<' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __ge__(self, other):
        if isinstance(other, self._base_type):
            return self._value_for_cmp >= other._value_for_cmp

        raise TypeError(
            "'>=' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __le__(self, other):
        if isinstance(other, self._base_type):
            return self._value_for_cmp <= other._value_for_cmp

        raise TypeError(
            "'<=' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")
