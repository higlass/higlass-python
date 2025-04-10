from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("higlass-python")
except PackageNotFoundError:
    __version__ = "uninstalled"


from higlass_schema import *

from higlass.api import (
    CombinedTrack,
    EnumTrack,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    PluginTrack,
    TrackT,
    View,
    Viewconf,
    ViewT,
    combine,
    concat,
    divide,
    hconcat,
    lock,
    track,
    vconcat,
    view,
)
from higlass.server import HiGlassServer
from higlass.tilesets import (
    Tileset,
    bed2ddb,
    beddb,
    bigwig,
    chromsizes,
    cooler,
    hitile,
    multivec,
    remote,
)

# a stub server with some helpful warnings
server = HiGlassServer()
