from ._version import __version__
from .viewer import display
from .tilesets import Tileset
from .server import Server
from .client import Track, CombinedTrack, View, ViewConf


def _jupyter_nbextension_paths():
    ViewConf(
        [
            View(
                [
                    Track(track_type="top-axis"),
                    Track(
                        track_type="pileup",
                        position="top",
                        data={"type": "bam", "url": "my_bam"},
                        options={"axisPositionHorizontal": "right"},
                    ),
                    Track(track_type="vcf", position="top", data={"type": "vcf", "url": "my_vcf"}),
                ]
            )
        ]
    ).to_dict()
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "higlass-jupyter",
            "require": "higlass-jupyter/extension",
        }
    ]
