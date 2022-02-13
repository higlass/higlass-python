import functools

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from higlass_schema import *

import hg.tilesets
from hg.api import *  # overrides classes with same name from higlass_schema
from hg.fuse import fuse
from hg.server import server
from hg.tilesets import remote


def register(tileset_fn):
    @functools.wraps(tileset_fn)
    def wrapper(*args, **kwargs):
        ts = tileset_fn(*args, **kwargs)
        return server.add(ts)

    return wrapper


bigwig = register(hg.tilesets.bigwig)
multivec = register(hg.tilesets.multivec)
cooler = register(hg.tilesets.cooler)
