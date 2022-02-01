from collections import defaultdict
from typing import Dict, List, Optional, Tuple, TypeVar, Union, overload
from typing_extensions import Literal

import slugid

from .core import (
    CombinedTrack,
    Data,
    EnumTrack,
    EnumTrackType,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    Layout,
    Lock,
    Track,
    Tracks,
    ValueScaleLock,
    View,
    Viewconf,
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
        data = defaultdict(list)
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


T = TypeVar("T", bound=Union[EnumTrack, HeatmapTrack])


def divide(t1: T, t2: T, **kwargs) -> T:
    assert t1.type == t2.type, "divided tracks must be same type"
    assert isinstance(t1.tilesetUid, str)
    assert isinstance(t1.server, str)

    assert isinstance(t2.tilesetUid, str)
    assert isinstance(t2.server, str)

    copy = t1.opts()  # copy first track with new uid
    copy.tilesetUid = None
    copy.server = None
    copy.data = Data(
        type="divided",
        children=[
            {
                "tilesetUid": track.tilesetUid,
                "server": track.server,
            }
            for track in (t1, t2)
        ],
    )
    # overrides
    for key, val in kwargs.items():
        setattr(copy, key, val)
    return copy


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


@overload
def lock(*views: View, **kwargs) -> Lock:
    ...


@overload
def lock(*pairs: Tuple[View, Track], **kwargs) -> ValueScaleLock:
    ...


def lock(*data, **kwargs):
    assert len(data) >= 1
    uid = str(slugid.nice())
    if isinstance(data[0], View):
        lck = Lock(uid=uid, **kwargs)
        for view in data:
            assert isinstance(view.uid, str)
            setattr(lck, view.uid, (1, 1, 1))
        return lck
    else:
        lck = ValueScaleLock(uid=uid, **kwargs)
        for view, track in data:
            assert isinstance(view.uid, str)
            assert isinstance(track.uid, str)
            vtuid = f"{view.uid}.{track.uid}"
            setattr(lck, vtuid, {"track": track.uid, "view": view.uid})
        return lck
