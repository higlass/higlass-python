from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"

from higlass_schema import *

import hg.tilesets
from hg.api import *  # overrides classes with same name from higlass_schema
from hg.fuse import fuse
from hg.server import server
from hg.tilesets import remote

bigwig = server.register(hg.tilesets.bigwig)
multivec = server.register(hg.tilesets.multivec)
cooler = server.register(hg.tilesets.cooler)
hitile = server.register(hg.tilesets.hitile)
bed2ddb = server.register(hg.tilesets.bed2ddb)
