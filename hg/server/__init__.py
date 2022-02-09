from typing import Dict, Optional

from hg.tilesets import LocalTileset

from ._provider import TilesetProvider, TilesetResource

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

    def enable_proxy(self):
        try:
            import jupyter_server_proxy
        except ImportError as e:
            raise ImportError(
                'Install "jupyter-server-proxy" to enable server proxying.'
            ) from e
        if not self._provider:
            self._provider = TilesetProvider().start()
        self._provider.proxy = True

    def disable_proxy(self):
        if not self._provider:
            raise RuntimeError("Server not started.")
        self._provider.proxy = False

    def add(
        self,
        tileset: LocalTileset,
        port: Optional[int] = None,
    ) -> TilesetResource:
        if self._provider is None:
            self._provider = TilesetProvider().start(port=port)

        if port is not None and port != self._provider.port:
            self._provider.stop().start(port=port)

        if tileset.uid not in self._tilesets:
            self._tilesets[tileset.uid] = self._provider.create(tileset)

        return self._tilesets[tileset.uid]

    def __rich_repr__(self):
        yield "tilesets", self._tilesets
        try:
            port = self.port
        except:
            port = None
        yield "port", port


server = HgServer()
