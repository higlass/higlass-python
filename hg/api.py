from typing import Optional, Dict, Literal, Tuple, Union
from enum import Enum
from .model import (
    View,
    Layout,
    Tracks,
    Track,
    HeatmapTrack,
    EnumTrack,
    EnumTrackType,
    IndependentViewportProjectionTrack,
)

import slugid

__all__ = ['view', 'track', 'Axis']

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

_datatype_default_track = {
    "2d-rectangle-domains": "2d-rectangle-domains",
    "bedlike": "bedlike",
    "chromsizes": "horizontal-chromosome-labels",
    "gene-annotations": "horizontal-gene-annotations",
    "matrix": "heatmap",
    "vector": "horizontal-bar",
    "multivec": "horizontal-multivec",
}

class Axis(Enum):
    right = 'top'
    left = 'left'

def view(
    *_tracks: Union[Track, Axis, Tuple[Track, TrackPosition]],
    layout: Optional[Layout] = None,
    tracks: Optional[Tracks] = None,
    uid: Optional[str] = None,
    **kwargs,
) -> View:

    layout = Layout() if layout is None else layout.copy()
    tracks = Tracks() if tracks is None else tracks.copy()

    for track in _tracks:
        if isinstance(track, tuple):
            track, position = track
        if isinstance(track, Axis):
            position = track.value
            track_type = 'top-axis' if position == 'top' else 'left-axis'
            track = EnumTrack(type=track_type)
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


def track(
    type: Union[EnumTrackType, Literal['heatmap']],
    fromViewUid: Optional[str] = None,
    **kwargs,
) -> Track:

    if type in {
        "viewport-projection-horizontal",
        "viewport-projection-vertical",
        "viewport-projection-center"
    } and fromViewUid is None:
        return IndependentViewportProjectionTrack(
            type=type, fromViewUid=fromViewUid, **kwargs # type: ignore
        )

    if type == 'heatmap':
        return HeatmapTrack(type=type, **kwargs)

    return EnumTrack(type=type, **kwargs)
