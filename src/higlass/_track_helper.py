from __future__ import annotations

import functools
import typing

from typing_extensions import ParamSpec

from higlass._protocols import TilesetResource, TilesetResourceFactory
from higlass._utils import datatype_default_track
from higlass.api import track

if typing.TYPE_CHECKING:
    from higlass.tilesets import LocalTileset, TrackType

__all__ = [
    "TrackHelper",
    "_bind_track_helper",
]


class TrackHelper:
    def __init__(self, resource: TilesetResource):
        self._resource = resource

    @property
    def tileset(self) -> LocalTileset:
        return self._resource.tileset

    @property
    def server(self) -> str:
        return self._resource.server

    def track(self, type_: TrackType | None = None, **kwargs):
        # use default track based on datatype if available
        if type_ is None:
            if getattr(self.tileset, "datatype", None) is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = typing.cast(
                    TrackType, datatype_default_track[self.tileset.datatype]
                )
        t = track(
            type_=type_,
            server=self.server,
            tilesetUid=self.tileset.uid,
            **kwargs,
        )
        if self.tileset.name:
            t.opts(name=self.tileset.name, inplace=True)
        return t


_P = ParamSpec("_P")


def _bind_track_helper(
    create_resource: TilesetResourceFactory,
    tileset_fn: typing.Callable[_P, LocalTileset],
) -> typing.Callable[_P, TrackHelper]:
    """Create a top-level helper function that adds the tileset to the factory."""

    @functools.wraps(tileset_fn)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> TrackHelper:
        tileset = typing.cast(typing.Any, tileset_fn)(*args, **kwargs)
        return TrackHelper(create_resource(tileset))

    return wrapper  # type: ignore
