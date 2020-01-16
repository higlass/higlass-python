from ._version import __version__
from .viewer import display
from .tilesets import Tileset
from .server import Server
from .client import Track, CombinedTrack, View, ViewConf


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "higlass-jupyter",
            "require": "higlass-jupyter/extension",
        }
    ]
