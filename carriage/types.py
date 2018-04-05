import attr


@attr.s(slots=True)
class CurrPrev:
    curr = attr.ib()
    prev = attr.ib()

    def __iter__(self):
        return iter(attr.astuple(self))


@attr.s(slots=True)
class CurrNext:
    curr = attr.ib()
    next = attr.ib()

    def __iter__(self):
        return iter(attr.astuple(self))


@attr.s(slots=True)
class ValueIndex:
    value = attr.ib()
    index = attr.ib()

    def __iter__(self):
        return iter(attr.astuple(self))
