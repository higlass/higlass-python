try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from higlass_schema import *

from .api import *  # overrides classes with same name from higlass_schema
from .fuse import fuse
from .server import server


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
