from __future__ import annotations

import typing
import weakref

from higlass._utils import resolve_tileset_uid

__all__ = ["TilesetProtocol", "TilesetRegistry"]


class TilesetRegistry:
    _registry: weakref.WeakValueDictionary[str, TilesetProtocol] = (
        weakref.WeakValueDictionary()
    )

    @classmethod
    def add(cls, tileset: TilesetProtocol) -> None:
        """Register a tileset with a given ID."""
        cls._registry[resolve_tileset_uid(tileset)] = tileset

    @classmethod
    def get(cls, tileset_id: str) -> TilesetProtocol:
        """Retrieve a tileset by its ID, or None if it no longer exists."""
        tileset = cls._registry.get(tileset_id)
        if tileset is None:
            raise KeyError(tileset_id)
        return tileset

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


class TilesetProtocol(typing.Protocol):
    def tiles(self, tile_ids: typing.Sequence[str]) -> list[typing.Any]: ...

    def info(self) -> typing.Any: ...
