from __future__ import annotations

import functools
import typing

from servir import Provider
from servir import TilesetResource as _TilesetResource
from typing_extensions import ParamSpec

from higlass._utils import datatype_default_track
from higlass.api import track
from higlass.tilesets import LocalTileset, TrackType

__all__ = [
    "HiGlassServer",
    "TilesetResource",
    "_create_tileset_helper",
]


class TilesetResource:
    def __init__(self, resource: _TilesetResource):
        self._resource = resource

    @property
    def tileset(self):
        return self._resource.tileset

    @property
    def server(self):
        return self._resource.server

    def track(self, type_: TrackType | None = None, **kwargs):
        # use default track based on datatype if available
        if type_ is None:
            if getattr(self.tileset, "datatype", None) is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = typing.cast(
                    TrackType, datatype_default_track[self.tileset.datatype]
                )
        t = track(
            type_=type_,
            server=self.server,
            tilesetUid=self.tileset.uid,
            **kwargs,
        )
        if self.tileset.name:
            t.opts(name=self.tileset.name, inplace=True)
        return t


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
            self._tilesets[tileset.uid] = TilesetResource(server_resource)

        return self._tilesets[tileset.uid]

    def __rich_repr__(self):
        yield "tilesets", self._tilesets
        try:
            port = self.port
        except RuntimeError:
            port = None
        yield "port", port


_P = ParamSpec("_P")


def _create_tileset_helper(
    server: HiGlassServer,
    tileset_fn: typing.Callable[_P, LocalTileset],
) -> typing.Callable[_P, TilesetResource]:
    """Create a top-level helper function that adds the tileset to the server."""

    @functools.wraps(tileset_fn)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> TilesetResource:
        tileset = typing.cast(typing.Any, tileset_fn)(*args, **kwargs)
        return server.add(tileset)

    return wrapper  # type: ignore
