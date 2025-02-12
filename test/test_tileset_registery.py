from __future__ import annotations

import typing

import pytest

from higlass._tileset_registry import TilesetRegistry
from higlass.tilesets import ClodiusTileset, register


def mock_tileset() -> ClodiusTileset:
    return ClodiusTileset(
        tiles_impl=lambda tile_ids: [],
        info_impl=lambda: {"min_pos": [0, 0], "max_pos": [100, 100]},
        datatype="multivec",
    )


@pytest.fixture
def Registry() -> typing.Generator[type[TilesetRegistry]]:
    yield TilesetRegistry
    TilesetRegistry.clear()


def test_tileset_registry(Registry: type[TilesetRegistry]) -> None:
    ts1 = mock_tileset()
    ts1_id = Registry.add(ts1)
    ts2 = mock_tileset()
    ts2_id = Registry.add(ts2)
    ts3 = mock_tileset()
    ts3_id = Registry.add(ts3)
    assert ts1 == Registry.get(ts1_id)
    assert ts2_id == Registry.add(ts2)
    assert ts3 == Registry.get(ts3_id)


def test_tilesets_are_weakly_referenced(Registry: type[TilesetRegistry]) -> None:
    uid = Registry.add(mock_tileset())
    with pytest.raises(KeyError):
        # need hard reference to tileset for it to stay in registry
        Registry.get(uid)


def test_custom_tileset_without_uid(Registry: type[TilesetRegistry]) -> None:
    @register
    class MyTileset:
        def tiles(self, tile_ids: typing.Sequence[str]) -> list[typing.Any]:
            return []

        def info(self) -> typing.Any:
            return {}

    ts = MyTileset()
    # doesn't create a tileset
    assert len(Registry._registry) == 0

    ts.track("heatmap")
    assert len(Registry._registry) == 1

    ts.track("heatmap")
    assert len(Registry._registry) == 1

    ts2 = MyTileset()
    ts2.track("heatmap")
    assert len(Registry._registry) == 2
