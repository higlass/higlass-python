import typing

import pytest

from higlass._tileset_registry import TilesetRegistry
from higlass.tilesets import LocalTileset


def mock_tileset(uid: str) -> LocalTileset:
    return LocalTileset(
        uid=uid or "mock_id",
        tiles=lambda tile_ids: [],
        info=lambda: {"min_pos": [0, 0], "max_pos": [100, 100]},
        datatype="multivec",
    )


@pytest.fixture(scope="module")
def registry() -> typing.Generator[type[TilesetRegistry]]:
    yield TilesetRegistry
    TilesetRegistry.clear()


def tileset_registry(registry: type[TilesetRegistry]) -> None:
    ts1 = mock_tileset(uid="mock_id_1")
    TilesetRegistry.add(ts1)
    ts2 = mock_tileset(uid="mock_id_2")
    TilesetRegistry.add(ts2)
    ts3 = mock_tileset(uid="mock_id_2")
    TilesetRegistry.add(ts3)
    assert ts1 == TilesetRegistry.get("mock_id_1")
    assert ts3 == TilesetRegistry.get("mock_id_2")
