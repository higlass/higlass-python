from __future__ import annotations

import typing
import weakref

__all__ = ["TilesetProtocol", "TilesetRegistry"]


class TilesetRegistry:
    _registry: weakref.WeakValueDictionary[str, TilesetProtocol] = (
        weakref.WeakValueDictionary()
    )

    @classmethod
    def add(cls, tileset: TilesetProtocol) -> str:
        """Register a tileset with a given ID."""
        uid = getattr(tileset, "uid", f"ts{id(tileset)}")
        cls._registry[uid] = tileset
        return uid

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
