from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"


from higlass_schema import *

import higlass.tilesets
from higlass._tileset_registry import create_jupyter_track_helper
from higlass.api import *
from higlass.fuse import fuse
from higlass.tilesets import remote

bigwig = create_jupyter_track_helper(higlass.tilesets.bigwig)
multivec = create_jupyter_track_helper(higlass.tilesets.multivec)
cooler = create_jupyter_track_helper(higlass.tilesets.cooler)
hitile = create_jupyter_track_helper(higlass.tilesets.hitile)
bed2ddb = create_jupyter_track_helper(higlass.tilesets.bed2ddb)
beddb = create_jupyter_track_helper(higlass.tilesets.beddb)
