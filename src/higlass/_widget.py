from __future__ import annotations

import concurrent.futures
import functools
import itertools
import json
import os
import pathlib
import typing

import anywidget
import ipywidgets
import pydantic
import traitlets as t

from higlass._tileset_registry import TilesetRegistry

__all__ = ["HiGlassWidget"]


class TilesetInfo(pydantic.BaseModel):
    """A tileset_info request payload."""

    type: typing.Literal["tileset_info"]
    tilesetUid: str


class Tiles(pydantic.BaseModel):
    """A tile request payload."""

    type: typing.Literal["tiles"]
    tileIds: list[str]


class CustomMessage(pydantic.BaseModel):
    """A custom message from the widget front end."""

    id: str
    payload: typing.Union[TilesetInfo, Tiles]  # noqa: UP007


class JupyterTilesetClient(ipywidgets.Widget):
    """A singleton client for handling tileset requests in a Jupyter environment.

    Requests are handled asynchronously using a thread pool executor.
    """

    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())

    def __init__(self) -> None:
        super().__init__()
        self.on_msg(self._handle_custom_message)

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_instance(cls):
        """Return a singleton client."""
        return cls()

    def _handle_custom_message(self, widget, msg, buffers):
        message = CustomMessage(**msg)

        def respond_with(payload: object):
            self.send({"id": message.id, "payload": payload})

        def process_message():
            if isinstance(message.payload, TilesetInfo):
                tileset_uid = message.payload.tilesetUid
                respond_with({tileset_uid: TilesetRegistry.get(tileset_uid).info()})

            elif isinstance(message.payload, Tiles):
                tile_ids = message.payload.tileIds
                tiles = []
                for tileset_uid, group in itertools.groupby(
                    iterable=sorted(tile_ids), key=lambda tile_id: tile_id.split(".")[0]
                ):
                    tiles.extend(TilesetRegistry.get(tileset_uid).tiles(list(group)))
                respond_with({tile_id: tile for tile_id, tile in tiles})

            else:
                raise RuntimeError("Unexpected execution path")

        self._executor.submit(process_message)


class HiGlassWidget(anywidget.AnyWidget):
    """An interactive anywidget for HiGlass."""

    _esm = pathlib.Path(__file__).parent / "widget.js"

    _viewconf = t.Dict(allow_none=False).tag(sync=True)
    _options = t.Dict().tag(sync=True)
    _plugin_urls = t.List().tag(sync=True)
    _tileset_client = t.Any().tag(sync=True, **ipywidgets.widget_serialization)

    # readonly properties
    location = t.List(t.Union([t.Float(), t.Tuple()]), read_only=True).tag(sync=True)

    def __init__(self, viewconf: dict, plugin_urls: list[str] | None, **viewer_options):
        super().__init__(
            _viewconf=viewconf,
            _plugin_urls=plugin_urls,
            _options=viewer_options,
            _tileset_client=JupyterTilesetClient.get_instance(),
        )

    def reload(self, *items):
        msg = json.dumps(["reload", items])
        self.send(msg)

    def zoom_to(
        self,
        view_id: str,
        start1: int,
        end1: int,
        start2: int | None = None,
        end2: int | None = None,
        animate_time: int = 500,
    ):
        msg = json.dumps(["zoomTo", view_id, start1, end1, start2, end2, animate_time])
        self.send(msg)
