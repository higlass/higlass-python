from __future__ import annotations

import functools
import pathlib
import typing
from dataclasses import dataclass
from typing import IO

import higlass.api
from higlass._tileset_registry import TilesetInfo, TilesetProtocol, TilesetRegistry
from higlass._utils import TrackType, datatype_default_track

__all__ = [
    "LocalTileset",
    "RemoteTileset",
    "bed2ddb",
    "bigwig",
    "cooler",
    "hitile",
    "multivec",
    "register",
    "remote",
]

DataType = typing.Literal["vector", "multivec", "matrix"]

T = typing.TypeVar("T", bound=TilesetProtocol)


def register(klass: type[T]) -> type[T]:
    """Decorator that adds a `track` method to a class implementing `TilesetProtocol`.

    The `track` method automatically registers the tileset with the `TilesetRegistry`
    and returns a HiGlass track object, which can be used for visualization.

    Parameters
    ----------
    klass : type[T]
        A class that implements `TilesetProtocol`.

    Returns
    -------
    type[T]
        The input class, now with an added `track` method.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from clodius.tiles.cooler import tiles, tileset_info
    >>>
    >>> @register
    >>> @dataclass
    >>> class MyCoolerTileset:
    >>>     filepath: str
    >>>     datatype = "matrix"
    >>>
    >>>     def info(self):
    >>>         return tileset_info(self.filepath)
    >>>
    >>>     def tiles(self, tile_ids):
    >>>         return tiles(self.filepath, tile_ids)
    >>>
    >>> tileset = MyCoolerTileset("test.mcool")
    >>> track = tileset.track("heatmap")
    """

    def track(
        self: TilesetProtocol, type_: TrackType | None = None, /, **kwargs
    ) -> higlass.api.Track:
        """
        Create a HiGlass track for the tileset.

        Registers the tileset with the `TilesetRegistry` and returns a track
        of the given `type_`. Defaults to a type based on the tileset's `datatype`
        if not specified.

        Parameters
        ----------
        type_ : TrackType, optional
            Track type. If `None`, a default is inferred.

        Returns
        -------
        higlass.api.Track
            The configured HiGlass track.
        """
        # use default track based on datatype if available
        if type_ is None:
            datatype = getattr(self, "datatype", None)
            if datatype is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = typing.cast(TrackType, datatype_default_track[datatype])

        # add tileset registry and get an identifier
        uid = TilesetRegistry.add(self)
        track = higlass.api.track(
            type_=type_,
            server="jupyter",
            tilesetUid=uid,
            **kwargs,
        )
        name = getattr(self, "name", None)
        if name is not None:
            track.opts(name=name, inplace=True)

        return track

    setattr(klass, "track", track)
    return klass


@register
class LocalTileset(TilesetProtocol):
    def __init__(
        self,
        datatype: DataType,
        tiles: typing.Callable[[typing.Sequence[str]], list[typing.Any]],
        info: typing.Callable[[], TilesetInfo],
        name: str | None = None,
    ):
        self.datatype = datatype
        self._tiles = tiles
        self._info = info
        self.name = name

    def tiles(self, tile_ids: typing.Sequence[str]) -> list[dict]:
        return self._tiles(tile_ids)

    def info(self) -> TilesetInfo:
        return self._info()


@dataclass
class RemoteTileset:
    uid: str
    server: str
    name: str | None = None

    def track(self, type_: TrackType, **kwargs):
        track = higlass.api.track(
            type_=type_,
            server=self.server,
            tilesetUid=self.uid,
            **kwargs,
        )
        if self.name is not None:
            track.opts(name=self.name, inplace=True)
        return track


def remote(uid: str, server: str = "https://higlass.io/api/v1", **kwargs):
    return RemoteTileset(uid, server, **kwargs)


def bigwig(filepath: str | pathlib.Path) -> LocalTileset:
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
    )


def beddb(filepath: str | pathlib.Path) -> LocalTileset:
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
    )


def multivec(filepath: str | pathlib.Path) -> LocalTileset:
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
    )


def cooler(filepath: str | pathlib.Path) -> LocalTileset:
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
    )


def hitile(filepath: str | pathlib.Path) -> LocalTileset:
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
    )


def bed2ddb(filepath: str | pathlib.Path) -> LocalTileset:
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
    )


by_filetype = {"cooler": cooler, "bigwig": bigwig}
