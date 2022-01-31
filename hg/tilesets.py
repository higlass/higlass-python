from typing import Any, Callable, Sequence, List, Dict, Optional
from dataclasses import dataclass

from .api import track, TrackType

import functools
import pathlib
import hashlib

TileId = str
Tile = Dict[str, Any]
TilesetInfo = Dict[str, Any]


@dataclass
class LocalTileset:
    tiles: Callable[[Sequence[TileId]], List[Tile]]
    info: Callable[[], TilesetInfo]
    uid: str
    type: Optional[str]


@dataclass
class RemoteTileset:
    uid: str
    server: str

    def track(self, type: TrackType, **kwargs):
        return track(
            type=type,
            server=self.server,
            tilesetUid=self.uid,
            **kwargs,
        )


def remote(uid: str, server: str = "//higlass.io/api/v1"):
    return RemoteTileset(uid, server)


def hash_absolute_filepath_as_default_uid(fn: Callable[[str, str], LocalTileset]):
    def wrapper(filepath: str, uid: str = None):
        if uid is None:
            abspath = pathlib.Path(filepath).absolute()
            uid = hashlib.md5(str(abspath).encode()).hexdigest()
        return fn(filepath, uid)

    return wrapper


@hash_absolute_filepath_as_default_uid
def beddb(filepath: str, uid: str):
    try:
        from clodius.tiles.beddb import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "beddb" data-server.'
        )

    return LocalTileset(
        type="beddb",
        tiles=functools.partial(tiles, filepath),
        info=functools.partial(tileset_info, filepath),
        uid=uid,
    )


@hash_absolute_filepath_as_default_uid
def bigwig(filepath: str, uid: str):
    try:
        from clodius.tiles.bigwig import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "vector" data-server.'
        )

    return LocalTileset(
        type="bigwig",
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
        type="multivec",
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
        type="cooler",
        tiles=functools.partial(tiles, filepath),
        info=functools.partial(tileset_info, filepath),
        uid=uid,
    )
