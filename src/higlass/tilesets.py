from __future__ import annotations

import functools
import hashlib
import pathlib
import typing
from dataclasses import dataclass
from typing import IO
from clodius.tiles.utils import tiles_wrapper_2d
from clodius.tiles.format import format_dense_tile

from ._utils import TrackType
from .api import track

__all__ = [
    "LocalTileset",
    "RemoteTileset",
    "remote",
    "bigwig",
    "multivec",
    "cooler",
    "hitile",
    "bed2ddb",
]

DataType = typing.Literal["vector", "multivec", "matrix"]


class LocalTileset:
    def __init__(
        self,
        datatype: DataType,
        tiles: typing.Callable[[typing.Sequence[str]], list[typing.Any]],
        info: typing.Callable[[], typing.Any],
        uid: str,
        name: str | None = None,
    ):
        self.datatype = datatype
        self._tiles = tiles
        self._info = info
        self._uid = uid
        self.name = name

    @property
    def uid(self) -> str:
        return self._uid

    def tiles(self, tile_ids: typing.Sequence[str]) -> list[typing.Any]:
        return self._tiles(tile_ids)

    def info(self) -> typing.Any:
        return self._info()


@dataclass
class RemoteTileset:
    uid: str
    server: str
    name: str | None = None

    def track(self, type_: TrackType, **kwargs):
        t = track(
            type_=type_,
            server=self.server,
            tilesetUid=self.uid,
            **kwargs,
        )
        if self.name:
            t.opts(name=self.name, inplace=True)
        return t


def remote(uid: str, server: str = "https://higlass.io/api/v1", **kwargs):
    return RemoteTileset(uid, server, **kwargs)


def hash_file_as_default_uid(fn: typing.Callable[[str | IO[bytes], str], LocalTileset]):
    def wrapper(file: str | IO[bytes], uid: None | str = None):
        if uid is None:
            if isinstance(file, str):
                abspath = pathlib.Path(file).absolute()
                uid = hashlib.md5(str(abspath).encode()).hexdigest()
            else:
                # File-like object likely provided
                uid = hashlib.md5(str(hash(file)).encode()).hexdigest()
        return fn(file, uid)

    return wrapper


@hash_file_as_default_uid
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


@hash_file_as_default_uid
def beddb(filepath: str, uid: str):
    try:
        from clodius.tiles.beddb import tiles, tileset_info
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


@hash_file_as_default_uid
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


@hash_file_as_default_uid
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


@hash_file_as_default_uid
def mrmatrix(filepath: str, uid: str):
    try:
        from clodius.tiles.mrmatrix import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "matrix" data-server.'
        )

    return LocalTileset(
        datatype="matrix",
        info=lambda: tileset_info(filepath),
        tiles=lambda tile_ids: tiles_wrapper_2d(
            tile_ids, lambda z, x, y: format_dense_tile(tiles(filepath, z, x, y))
        ),
        uid=uid,
    )


@hash_file_as_default_uid
def hitile(filepath: str, uid: str):
    try:
        from clodius.tiles.hitile import tiles, tileset_info
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


@hash_file_as_default_uid
def bed2ddb(filepath: str, uid: str):
    try:
        from clodius.tiles.bed2ddb import tiles, tileset_info
    except ImportError:
        raise ImportError(
            'You must have `clodius` installed to use "vector" data-server.'
        )

    return LocalTileset(
        datatype="2d-rectangle-domains",
        tiles=functools.partial(tiles, filepath),
        info=functools.partial(tileset_info, filepath),
        uid=uid,
    )


by_filetype = {"cooler": cooler, "bigwig": bigwig, "mrmatrix": mrmatrix}
