from __future__ import annotations

import json
import pathlib

import anywidget
import traitlets as t
import ipywidgets


class HiGlassWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "widget.js"

    _viewconf = t.Dict(allow_none=False).tag(sync=True)
    _options = t.Dict().tag(sync=True)
    _ts = t.Any().tag(sync=True, **ipywidgets.widget_serialization)

    # readonly properties
    location = t.List(t.Union([t.Float(), t.Tuple()]), read_only=True).tag(sync=True)

    def __init__(self, viewconf: dict, ts, **viewer_options):
        super().__init__(_viewconf=viewconf, _ts=ts, _options=viewer_options)

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
