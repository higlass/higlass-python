try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from higlass_schema import *

from .api import * # overrides classes with same name from higlass_schema
from .server import HgServer, server
