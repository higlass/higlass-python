from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"

from higlass_schema import *

import higlass.tilesets
from higlass.api import *  # overrides classes with same name from higlass_schema
from higlass.fuse import fuse
from higlass.server import server
from higlass.tilesets import remote

bigwig = server.register(higlass.tilesets.bigwig)
multivec = server.register(higlass.tilesets.multivec)
cooler = server.register(higlass.tilesets.cooler)
hitile = server.register(higlass.tilesets.hitile)
bed2ddb = server.register(higlass.tilesets.bed2ddb)
