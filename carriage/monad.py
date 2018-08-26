from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty


class Monad(ABC):

    @abstractclassmethod
    def unit(cls, value):
        raise NotImplementedError()

    @abstractmethod
    def flat_map(self, to_monad_action):
        raise NotImplementedError()

    def bind(self, to_monad_action):
        return self.flat_map(to_monad_action)

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
    def then(self, monad_value):
        raise NotImplementedError()

    @abstractmethod
    def ap(self, monad_value):
        raise NotImplementedError()

    @abstractmethod
    def pluck(self, key):
        raise NotImplementedError()

    @abstractmethod
    def pluck_opt(self, key):
        raise NotImplementedError()

    @abstractmethod
    def pluck_attr(self, attr):
        raise NotImplementedError()

    # @abstractmethod
    # def __len__(self):
    #     raise NotImplementedError()

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()

    @abstractproperty
    def _base_type(self):
        raise NotImplementedError()

    @abstractproperty
    def _comparing_value(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, self._base_type):
            return self._comparing_value == other._comparing_value

        raise TypeError(
            "'==' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __ne__(self, other):
        if isinstance(other, self._base_type):
            return self._comparing_value != other._comparing_value

        raise TypeError(
            "'!=' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __gt__(self, other):
        if isinstance(other, self._base_type):
            return self._comparing_value > other._comparing_value

        raise TypeError(
            "'>' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __lt__(self, other):
        if isinstance(other, self._base_type):
            return self._comparing_value < other._comparing_value

        raise TypeError(
            "'<' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __ge__(self, other):
        if isinstance(other, self._base_type):
            return self._comparing_value >= other._comparing_value

        raise TypeError(
            "'>=' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")

    def __le__(self, other):
        if isinstance(other, self._base_type):
            return self._comparing_value <= other._comparing_value

        raise TypeError(
            "'<=' not supported between instances of "
            f"'{self._base_type.__name__}' and {type(other).__name__!r}")
