from typing import Dict, List, Literal, Optional, Tuple, Union, Any
from copy import deepcopy
from collections import defaultdict

import slugid

from .core import (
    CombinedTrack,
    DividedTrack,
    EnumTrack,
    EnumTrackType,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    Layout,
    Track,
    Tracks,
    View,
    Viewconf,
    Tileset,
    Lock,
)

TrackPosition = Literal["center", "top", "left", "bottom", "center", "whole", "gallery"]

_track_default_position: Dict[str, TrackPosition] = {
    "2d-rectangle-domains": "center",
    "bedlike": "top",
    "horizontal-bar": "top",
    "horizontal-chromosome-labels": "top",
    "chromosome-labels": "top",
    "horizontal-gene-annotations": "top",
    "horizontal-heatmap": "top",
    "horizontal-1d-heatmap": "top",
    "horizontal-line": "top",
    "horizontal-multivec": "top",
    "bar": "top",
    "chromosome-labels": "top",
    "gene-annotations": "top",
    "heatmap": "top",
    "1d-heatmap": "top",
    "line": "top",
    "horizontal-multivec": "top",
    "heatmap": "center",
    "left-axis": "left",
    "osm-tiles": "center",
    "top-axis": "top",
    "viewport-projection-center": "center",
    "viewport-projection-horizontal": "top",
}

TrackType = Union[EnumTrackType, Literal["heatmap"]]


def track(
    type: TrackType,
    uid: Optional[str] = None,
    fromViewUid: Optional[str] = None,
    **kwargs,
) -> Track:
    if uid is None:
        uid = str(slugid.nice())

    if (
        type
        in {
            "viewport-projection-horizontal",
            "viewport-projection-vertical",
            "viewport-projection-center",
        }
        and fromViewUid is None
    ):
        return IndependentViewportProjectionTrack(
            type=type, uid=uid, fromViewUid=fromViewUid, **kwargs  # type: ignore
        )

    if type == "heatmap":
        return HeatmapTrack(type=type, uid=uid, **kwargs)

    return EnumTrack(type=type, uid=uid, **kwargs)


def view(
    *_tracks: Union[Track, Tracks, Tuple[Track, TrackPosition]],
    x: int = 0,
    y: int = 0,
    width: int = 12,
    height: int = 6,
    tracks: Optional[Tracks] = None,
    layout: Optional[Layout] = None,
    uid: Optional[str] = None,
    **kwargs,
) -> View:

    if layout is None:
        layout = Layout(x=x, y=y, w=width, h=height)
    else:
        layout = Layout(**layout.dict())

    if tracks is None:
        data  = defaultdict(list)
    else:
        data = defaultdict(list, tracks.dict())

    for track in _tracks:
        if isinstance(track, Tracks):
            track = track.dict()
            for position, track_list in track.items():
                data[position].extend(track_list)
        else:
            if isinstance(track, tuple):
                track, position = track
            else:
                if track.type is None:
                    raise ValueError("No default track type")
                position = _track_default_position[track.type]
            data[position].append(track)

    if uid is None:
        uid = str(slugid.nice())

    return View(
        layout=layout,
        tracks=Tracks(**data),
        uid=uid,
        **kwargs,
    )


def combine(t1: Track, t2: Track, uid: Optional[str] = None, **kwargs) -> CombinedTrack:
    if uid is None:
        uid = str(slugid.nice())

    if isinstance(t1, CombinedTrack):
        copy = CombinedTrack(**t1.dict())
        copy.contents.append(t2.__class__(**t2.dict()))
        for key, val in kwargs.items():
            setattr(copy, key, val)
        return copy

    return CombinedTrack(
        type="combined",
        uid=uid,
        contents=[track.__class__(**track.dict()) for track in (t1, t2)],
        **kwargs,
    )


def divide(
    t1: Track,
    t2: Track,
    uid: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> DividedTrack:
    assert t1.type == t2.type, "divided tracks must be same type"

    if options is None:
        # TODO: add logging warning
        if isinstance(t1.options, dict):
            options = deepcopy(t1.options)
        else:
            options = {}
    else:
        options = deepcopy(options)

    if isinstance(options, dict):
        options = deepcopy(options)

    children = [
        Tileset(
            tilesetUid=track.tilesetUid,  # type: ignore
            server=track.server,  # type: ignore
        )
        for track in (t1, t2)
    ]

    return DividedTrack(
        type="divided",
        uid=uid,
        options=options,
        children=children,
        **kwargs,
    )


def project(
    position: Literal["center", "top", "bottom", "left", "right"],
    view: Optional[View] = None,
    **kwargs,
):
    if view is None:
        fromViewUid = None
    else:
        assert isinstance(view.uid, str)
        fromViewUid = view.uid

    if position == "center":
        track_type = "viewport-projection-center"
    elif position == "top" or position == "bottom":
        track_type = "viewport-projection-horizontal"
    elif position == "left" or position == "right":
        track_type = "viewport-projection-vertical"
    else:
        raise ValueError("Not possible")

    return track(type=track_type, fromViewUid=fromViewUid, **kwargs)


def viewconf(
    *_views: View,
    views: Optional[List[View]] = None,
    trackSourceServers: Optional[List[str]] = None,
    editable: bool = True,
    exportViewUrl: str = "http://higlass.io/api/v1/viewconfs",
    **kwargs,
):
    views = [] if views is None else [View(**v.dict()) for v in views]

    for view in _views:
        views.append(View(**view.dict()))

    if trackSourceServers is None:
        trackSourceServers = ["http://higlass.io/api/v1"]

    return Viewconf(
        views=views,
        editable=editable,
        exportViewUrl=exportViewUrl,
        trackSourceServers=trackSourceServers,
        **kwargs,
    )


def lock(*views: View, **kwargs):
    lck = Lock(uid=str(slugid.nice()), **kwargs)
    for view in views:
        assert isinstance(view.uid, str)
        setattr(lck, view.uid, (1, 1, 1))
    return lck
