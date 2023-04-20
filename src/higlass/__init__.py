from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"


from higlass_schema import *

import higlass.tilesets
from higlass.api import *
from higlass.fuse import fuse
from higlass.server import HiGlassServer, _create_tileset_helper
from higlass.tilesets import remote

server = HiGlassServer()

bigwig = _create_tileset_helper(server, higlass.tilesets.bigwig)
multivec = _create_tileset_helper(server, higlass.tilesets.multivec)
cooler = _create_tileset_helper(server, higlass.tilesets.cooler)
hitile = _create_tileset_helper(server, higlass.tilesets.hitile)
bed2ddb = _create_tileset_helper(server, higlass.tilesets.bed2ddb)
