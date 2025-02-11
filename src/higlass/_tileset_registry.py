from __future__ import annotations

import typing
import weakref

from higlass._protocols import TilesetResource

if typing.TYPE_CHECKING:
    from higlass.tilesets import LocalTileset


__all__ = [
    "TilesetRegistry",
    "create_jupyter_resource",
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


class JupyterTilesetResource(TilesetResource):
    def __init__(self, tileset: LocalTileset):
        self._tileset = tileset

    @property
    def tileset(self):
        return self._tileset

    @property
    def server(self):
        return "jupyter"


def create_jupyter_resource(tileset: LocalTileset) -> JupyterTilesetResource:
    TilesetRegistry.add(tileset)
    return JupyterTilesetResource(tileset)
