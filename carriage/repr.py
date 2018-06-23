import reprlib

short_repr = reprlib.Repr()
short_repr.maxlist = 10
short_repr.maxset = 10
short_repr.maxdict = 10
short_repr.maxtuple = 10
short_repr.maxset = 10
short_repr.maxfrozenset = 10
short_repr.maxdeque = 10
short_repr.maxarray = 10
short_repr.maxlong = 20
short_repr.maxstring = 20
short_repr.maxother = 30


def repr_args(*args, **kwargs):
    args_str = ', '.join(repr(arg) for arg in args)
    kwargs_str = ', '.join(f'{k}={v!r}' for k, v in kwargs.items())
    if args_str and kwargs_str:
        return f'{args_str}, {kwargs_str}'
    elif args_str:
        return args_str
    else:
        return kwargs_str
