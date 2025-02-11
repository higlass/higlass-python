from __future__ import annotations

import typing

from servir import Provider, TilesetResource

if typing.TYPE_CHECKING:
    from higlass.tilesets import LocalTileset

__all__ = ["HiGlassServer"]


class HiGlassServer:
    def __init__(self):
        self._provider: Provider | None = None
        # We need to keep references to served resources,
        # because the background server uses weakrefs.
        self._tilesets: dict[str, TilesetResource] = {}

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
            import jupyter_server_proxy  # noqa: F401
        except ImportError as e:
            raise ImportError(
                'Install "jupyter-server-proxy" to enable server proxying.'
            ) from e
        if not self._provider:
            self._provider = Provider().start()
        self._provider.proxy = True

    def disable_proxy(self):
        if not self._provider:
            raise RuntimeError("Server not started.")
        self._provider.proxy = False

    def add(
        self,
        tileset: LocalTileset,
        port: int | None = None,
    ) -> TilesetResource:
        """Add a tileset to the server.

        Note: Only tilesets with new uids are added to the server. If the tileset
              uid matches one already on the server, the existing tileset resource
              is returned. Existing tilesets can only be cleared with
              `HiGlassServer.reset()`.
        """
        if self._provider is None:
            self._provider = Provider().start(port=port)

        if port is not None and port != self._provider.port:
            self._provider.stop().start(port=port)

        if tileset.uid not in self._tilesets:
            server_resource = self._provider.create(tileset)
            self._tilesets[tileset.uid] = server_resource

        return self._tilesets[tileset.uid]

    def __rich_repr__(self):
        yield "tilesets", self._tilesets
        try:
            port = self.port
        except RuntimeError:
            port = None
        yield "port", port
