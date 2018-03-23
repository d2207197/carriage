
class Maybe():
    @classmethod
    def none(cls, value):
        if value is None:
            return Nothing
        return Just(value)

    @classmethod
    def exception(cls, get_value, errors=Exception):
        try:
            value = get_value()
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

none = Maybe.none
exception = Maybe.exception

class _Nothing(Maybe):    
    def __repr__(self):
        return "Nothing"

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


Nothing = _Nothing()


class Just(Maybe):
    def __init__(self, v):
        self.value = v

    def __repr__(self):
        return f"Just({self.value!r})"

    def then_maybe(self, action):
        value = action(self.value)
        if isinstance(value, Maybe):
            return value
        else:
            raise TypeError('function should return a Maybe')
    
    def then(self, action):
        return Just(action(self.value))

    def get_or(self, else_value):
        return self.value


    def is_just(self):
        return True

    def is_nothing(self):
        return False



