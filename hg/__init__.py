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

# https://github.com/bqplot/bqplot/blob/e9bae6f3447e2d173112b133406a52e6537c32ee/bqplot/__init__.py#L72-L81
def _prefix():
    import sys
    from pathlib import Path

    prefix = sys.prefix
    here = Path(__file__).parent
    # for when in dev mode
    if (here.parent / "share/jupyter/nbextensions/hg").parent.exists():
        prefix = str(here.parent)
    return prefix


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": _prefix() + "/share/jupyter/nbextensions/hg/",
            "dest": "hg",
            "require": "hg/extension",
        }
    ]
