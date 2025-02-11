from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"


from higlass_schema import *

import higlass.tilesets
from higlass._display import renderers
from higlass._tileset_registry import create_jupyter_resource
from higlass._track_helper import _bind_track_helper
from higlass.api import *
from higlass.fuse import fuse
from higlass.tilesets import remote

# from higlass.server import HiGlassServer
# server = HiGlassServer()

server = create_jupyter_resource

bigwig = _bind_track_helper(server, higlass.tilesets.bigwig)
multivec = _bind_track_helper(server, higlass.tilesets.multivec)
cooler = _bind_track_helper(server, higlass.tilesets.cooler)
hitile = _bind_track_helper(server, higlass.tilesets.hitile)
bed2ddb = _bind_track_helper(server, higlass.tilesets.bed2ddb)
beddb = _bind_track_helper(server, higlass.tilesets.beddb)
