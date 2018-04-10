
import reprlib

from .array import Array
from .map import Map
from .optional import Nothing, NothingError, Optional, Some
from .stream import Stream

reprlib.aRepr.maxlist = 5
reprlib.aRepr.maxset = 5
reprlib.aRepr.maxdict = 5
reprlib.aRepr.maxtuple = 5
reprlib.aRepr.maxset = 5
reprlib.aRepr.maxfrozenset = 5
reprlib.aRepr.maxdeque = 5
reprlib.aRepr.maxarray = 5
reprlib.aRepr.maxlong = 20
reprlib.aRepr.maxstring = 20
reprlib.aRepr.maxother = 30

__all__ = ['Optional', 'Some', 'Nothing',
           'NothingError', 'Stream', 'Array', 'Map']
