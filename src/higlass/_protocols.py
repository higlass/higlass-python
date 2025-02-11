from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from higlass.tilesets import LocalTileset


__all__ = ["TilesetResource", "TilesetResource"]


class TilesetResource(typing.Protocol):
    @property
    def tileset(self) -> LocalTileset: ...

    @property
    def server(self) -> str: ...


class TilesetResourceFactory(typing.Protocol):
    def __call__(self, tileset: LocalTileset) -> TilesetResource: ...
