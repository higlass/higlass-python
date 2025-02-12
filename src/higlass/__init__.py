from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"


from higlass_schema import *

import higlass.tilesets as tilesets
from higlass.api import *
from higlass.server import HiGlassServer
from higlass.tilesets import bed2ddb, beddb, bigwig, cooler, hitile, multivec, remote

# a stub server with some helpful warnings
server = HiGlassServer()
