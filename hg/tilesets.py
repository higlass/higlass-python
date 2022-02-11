import functools
import hashlib
import pathlib
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

from typing_extensions import Literal

from .api import track
from .utils import TrackType

TileId = str
Tile = Dict[str, Any]
TilesetInfo = Dict[str, Any]

DataType = Literal["vector", "multivec", "matrix"]


@dataclass
class LocalTileset:
    tiles: Callable[[Sequence[TileId]], List[Tile]]
    info: Callable[[], TilesetInfo]
    uid: str
    datatype: Optional[DataType] = None


@dataclass
class RemoteTileset:
    uid: str
    server: str

    def track(self, type_: TrackType, **kwargs):
        return track(
            type_=type_,
            server=self.server,
            tilesetUid=self.uid,
            **kwargs,
        )


def remote(uid: str, server: str = "https://higlass.io/api/v1"):
    return RemoteTileset(uid, server)


def hash_absolute_filepath_as_default_uid(fn: Callable[[str, str], LocalTileset]):
    def wrapper(filepath: str, uid: str = None):
        if uid is None:
            abspath = pathlib.Path(filepath).absolute()
            uid = hashlib.md5(str(abspath).encode()).hexdigest()
        return fn(filepath, uid)

    return wrapper


@hash_absolute_filepath_as_default_uid
def bigwig(filepath: str, uid: str):
    try:
        from clodius.tiles.bigwig import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "vector" data-server.'
        )

    return LocalTileset(
        datatype="vector",
        tiles=functools.partial(tiles, filepath),
        info=functools.partial(tileset_info, filepath),
        uid=uid,
    )


@hash_absolute_filepath_as_default_uid
def multivec(filepath: str, uid: str):
    try:
        from clodius.tiles.multivec import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "multivec" data-server.'
        )

    return LocalTileset(
        datatype="multivec",
        tiles=functools.partial(tiles, filepath),
        info=functools.partial(tileset_info, filepath),
        uid=uid,
    )


@hash_absolute_filepath_as_default_uid
def cooler(filepath: str, uid: str):
    try:
        from clodius.tiles.cooler import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "matrix" data-server.'
        )

    return LocalTileset(
        datatype="matrix",
        tiles=functools.partial(tiles, filepath),
        info=functools.partial(tileset_info, filepath),
        uid=uid,
    )
