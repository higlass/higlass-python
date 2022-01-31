from typing import Dict, Optional

from hg.tilesets import LocalTileset

from ._provider import TilesetProvider, TilesetResource

__all__ = [
    "HgServer",
    "server",
]


class HgServer:
    def __init__(self):
        self._provider: Optional[TilesetProvider] = None
        # We need to keep references to served resources,
        # because the background server uses weakrefs.
        self._tilesets: Dict[str, TilesetResource] = {}

    @property
    def port(self):
        if not self._provider:
            raise RuntimeError("Server not started.")
        return self._provider.port

    def reset(self) -> None:
        if self._provider is not None:
            self._provider.stop()
        self._resources = {}

    def add(
        self,
        tileset: LocalTileset,
        port: Optional[int] = None,
    ) -> TilesetResource:
        if self._provider is None:
            self._provider = TilesetProvider(allowed_origins=["*"]).start(port=port)

        if port is not None and port != self._provider.port:
            self._provider.stop().start(port=port)

        if tileset.uid not in self._resources:
            self._resources[tileset.uid] = self._provider.create(tileset)

        return self._resources[tileset.uid]

    def __rich_repr__(self):
        yield "tilesets", self._tilesets
        try:
            port = self.port
        except:
            port = None
        yield "port", port


server = HgServer()
