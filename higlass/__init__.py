from ._version import __version__
from .client import CombinedTrack, Track, View, ViewConf
from .server import Server
from .tilesets import Tileset
from .viewer import display


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "higlass-jupyter",
            "require": "higlass-jupyter/extension",
        }
    ]
