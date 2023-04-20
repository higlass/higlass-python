from __future__ import annotations

import typing

import pytest

from higlass.server import HiGlassServer
from higlass.tilesets import LocalTileset


def mock_tileset(uid: str) -> LocalTileset:
    return LocalTileset(
        uid=uid or "mock_id",
        tiles=lambda tile_ids: [],
        info=lambda: {"min_pos": [0, 0], "max_pos": [100, 100]},
        datatype="multivec",
    )


@pytest.fixture(scope="module")
def server() -> typing.Iterator[HiGlassServer]:
    server = HiGlassServer()
    yield server
    server.reset()


def test_server(server: HiGlassServer) -> None:
    with pytest.raises(RuntimeError):
        server.port

    ts = mock_tileset(uid="mock_id_1")
    server.add(ts)
    assert server.port > 0
    assert len(server._tilesets) == 1

    ts = mock_tileset(uid="mock_id_2")
    server.add(ts)
    assert len(server._tilesets) == 2


def test_proxy(server: HiGlassServer) -> None:
    ts = mock_tileset(uid="mock_id_3")
    resource = server.add(ts)
    assert f"http://localhost:{server.port}/tilesets/api/v1/" == resource.server
    server.enable_proxy()
    assert f"/proxy/{server.port}/tilesets/api/v1/" == resource.server
