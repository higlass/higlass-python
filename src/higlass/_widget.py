from __future__ import annotations

import concurrent.futures
import itertools
import json
import os
import pathlib
import typing

import anywidget
import ipywidgets
import traitlets as t

from higlass._tileset_registry import TilesetRegistry

if typing.TYPE_CHECKING:
    from higlass.tilesets import LocalTileset

__all__ = ["HiGlassWidget"]

THREAD_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())


def get_tileset(tileset_uid: str) -> LocalTileset:
    tileset = TilesetRegistry.get(tileset_uid)
    assert tileset, f"No tileset registered with id: {tileset_uid}"
    return tileset


def handle_custom_msg(widget, msg, buffers):
    def respond_with(payload):
        widget.send({"id": msg["id"], "payload": payload})

    def target():
        match msg["payload"]:
            case {"type": "tileset_info", "tilesetUid": tileset_uid}:
                respond_with({tileset_uid: get_tileset(tileset_uid).info()})
            case {"type": "tiles", "tileIds": tile_ids}:
                tiles = []
                for tileset_uid, group_tile_ids in itertools.groupby(
                    iterable=sorted(tile_ids), key=lambda tile_id: tile_id.split(".")[0]
                ):
                    tiles.extend(get_tileset(tileset_uid).tiles(list(group_tile_ids)))
                respond_with({tile_id: tile for tile_id, tile in tiles})
            case _:
                message = f"Invalid request, got: {msg.get('type', 'unknown')}"
                raise ValueError(message)

    THREAD_EXECUTOR.submit(target)


class TilesetClient(ipywidgets.DOMWidget):
    def __init__(self):
        super().__init__()
        self.on_msg(handle_custom_msg)


# a singleton for all the tilesets
_TILESET_CLIENT = TilesetClient()


class HiGlassWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "widget.js"

    _viewconf = t.Dict(allow_none=False).tag(sync=True)
    _options = t.Dict().tag(sync=True)
    _tileset_client = t.Any().tag(sync=True, **ipywidgets.widget_serialization)
    _plugin_urls = t.List().tag(sync=True)

    # readonly properties
    location = t.List(t.Union([t.Float(), t.Tuple()]), read_only=True).tag(sync=True)

    def __init__(self, viewconf: dict, plugin_urls: list[str] | None, **viewer_options):
        super().__init__(
            _viewconf=viewconf,
            _tileset_client=_TILESET_CLIENT,
            _plugin_urls=plugin_urls,
            _options=viewer_options,
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
