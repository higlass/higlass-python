from __future__ import annotations

import typing
import weakref

__all__ = ["TilesetInfo", "TilesetProtocol", "TilesetRegistry"]


class Transform(typing.TypedDict):
    name: str
    value: str


class TilesetInfo(typing.TypedDict):
    resolutions: tuple[int, ...]
    transforms: list[Transform]
    max_pos: list[int]
    min_pos: list[int]
    chromsizes: list[tuple[str, int]]


class TilesetProtocol(typing.Protocol):
    def tiles(self, *, tile_ids: typing.Sequence[str]) -> list[dict]: ...

    def info(self) -> TilesetInfo: ...


class TilesetRegistry:
    _registry = weakref.WeakValueDictionary[str, TilesetProtocol]()

    @classmethod
    def add(cls, tileset: TilesetProtocol) -> str:
        """Register a tileset with a given ID."""
        uid = f"hg_{id(tileset):x}"
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
