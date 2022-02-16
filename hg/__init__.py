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

bigwig = server.register(hg.tilesets.bigwig)
multivec = server.register(hg.tilesets.multivec)
cooler = server.register(hg.tilesets.cooler)
