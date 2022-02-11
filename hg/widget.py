import json
from collections import defaultdict
from typing import Union

from .api import TrackT, View, Viewconf

try:
    import ipywidgets
    import traitlets.traitlets as t
except ImportError as e:
    raise ImportError('Install "ipywidgets" to use hg.widget') from e


class HgWidget(ipywidgets.DOMWidget):
    _model_name = t.Unicode("HgModel").tag(sync=True)
    _model_module = t.Unicode("hg").tag(sync=True)
    _model_module_version = t.Unicode("0.0.0").tag(sync=True)

    _view_name = t.Unicode("HgView").tag(sync=True)
    _view_module = t.Unicode("hg").tag(sync=True)
    _view_module_version = t.Unicode("0.0.0").tag(sync=True)

    _viewconf = t.Unicode("null").tag(sync=True)

    # readonly properties
    location = t.List(t.Union([t.Float(), t.Tuple()]), read_only=True).tag(sync=True)

    def __init__(self, viewconf: Viewconf, **kwargs):
        super().__init__(**kwargs)
        self._viewconf = viewconf.json()

        self._mapping = defaultdict(list)
        for view in viewconf.views:
            for _, track in view.tracks:
                self._mapping[track.uid].append(view.uid)

    def reload(self, *items: Union[View, TrackT]):
        selectors = []
        for i in items:
            if isinstance(i, View):
                selectors.append(i.uid)
            else:
                for vuid in self._mapping[i.uid]:
                    sel = dict(viewId=vuid, trackId=i.uid)
                    selectors.append(sel)

        msg = json.dumps(["reload", selectors])
        self.send(msg)

    def zoom_to(
        self,
        view: Union[View, str],
        start1: int,
        end1: int,
        start2: int = None,
        end2: int = None,
        animate_time: int = 500,
    ):
        uid = view if isinstance(view, str) else view.uid
        assert uid is not None, "must provide a view uid"
        msg = json.dumps(["zoomTo", uid, start1, end1, start2, end2, animate_time])
        self.send(msg)
