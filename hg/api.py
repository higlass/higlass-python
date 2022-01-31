from typing import Dict, List, Literal, Optional, Tuple, Union

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
    TrackLayout,
    View,
    Viewconf,
    Tileset,
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
    *_tracks: Union[Track, Tuple[Track, TrackPosition]],
    layout: Optional[Layout] = None,
    tracks: Optional[TrackLayout] = None,
    uid: Optional[str] = None,
    **kwargs,
) -> View:

    layout = Layout() if layout is None else layout.copy()
    tracks = TrackLayout() if tracks is None else tracks.copy()

    for track in _tracks:
        if isinstance(track, tuple):
            track, position = track
        else:
            if track.type is None:
                raise ValueError("No default track type")
            position = _track_default_position[track.type]

        if getattr(tracks, position) is None:
            setattr(tracks, position, [])

        getattr(tracks, position).append(track)

    if uid is None:
        uid = str(slugid.nice())

    return View(
        layout=layout,
        tracks=tracks,
        uid=uid,
        **kwargs,
    )


def combine(t1: Track, t2: Track, uid: Optional[str] = None, **kwargs) -> CombinedTrack:
    if uid is None:
        uid = str(slugid.nice())

    if isinstance(t1, CombinedTrack):
        copy = t1.copy()
        t1.contents.append(t2.copy())
        for key, val in kwargs.items():
            setattr(copy, key, val)
        return copy

    return CombinedTrack(
        type="combined",
        uid=uid,
        contents=[t1.copy(), t2.copy()],
        **kwargs,
    )


def divide(t1: Track, t2: Track, uid: Optional[str] = None, **kwargs) -> DividedTrack:
    assert t1.type == t2.type, "divided tracks must be same type"
    if "options" in kwargs:
        options = kwargs["options"]
    else:
        # TODO: add logging warning
        options = t1.options

    if uid is None:
        uid = str(slugid.nice())

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
    views = [] if views is None else [v.copy() for v in views]

    for v in _views:
        views.append(v.copy())

    if trackSourceServers is None:
        trackSourceServers = ["http://higlass.io/api/v1"]

    return Viewconf(
        views=views,
        editable=editable,
        exportViewUrl=exportViewUrl,
        trackSourceServers=trackSourceServers,
        **kwargs,
    )
