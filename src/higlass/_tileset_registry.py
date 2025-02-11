from __future__ import annotations

import functools
import typing
import weakref
from dataclasses import dataclass

from typing_extensions import ParamSpec

import higlass.api
from higlass._utils import datatype_default_track

if typing.TYPE_CHECKING:
    from higlass.tilesets import LocalTileset, TrackType


__all__ = [
    "JupyterTrackHelper",
    "TilesetRegistry",
    "create_jupyter_track_helper",
]


class TilesetRegistry:
    _registry: weakref.WeakValueDictionary[str, LocalTileset] = (
        weakref.WeakValueDictionary()
    )

    @classmethod
    def add(cls, tileset: LocalTileset) -> None:
        """Register a tileset with a given ID."""
        cls._registry[tileset.uid] = tileset

    @classmethod
    def get(cls, tileset_id: str) -> LocalTileset:
        """Retrieve a tileset by its ID, or None if it no longer exists."""
        tileset = cls._registry.get(tileset_id)
        if tileset is None:
            raise KeyError(tileset_id)
        return tileset

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


@dataclass(frozen=True)
class JupyterTrackHelper:
    tileset: LocalTileset

    def track(self, type_: TrackType | None = None, **kwargs):
        # use default track based on datatype if available
        if type_ is None:
            if getattr(self.tileset, "datatype", None) is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = typing.cast(
                    TrackType, datatype_default_track[self.tileset.datatype]
                )
        track = higlass.api.track(
            type_=type_,
            server="jupyter",
            tilesetUid=self.tileset.uid,
            **kwargs,
        )
        if self.tileset.name:
            track.opts(name=self.tileset.name, inplace=True)
        return track


_P = ParamSpec("_P")


def create_jupyter_track_helper(
    tileset_fn: typing.Callable[_P, LocalTileset],
) -> typing.Callable[_P, JupyterTrackHelper]:
    """Create a top-level helper function that adds the tileset to the factory."""

    @functools.wraps(tileset_fn)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> JupyterTrackHelper:
        tileset = tileset_fn(*args, **kwargs)
        TilesetRegistry.add(tileset)
        return JupyterTrackHelper(tileset)

    return wrapper  # type: ignore
