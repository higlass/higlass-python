from collections import defaultdict
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
    ClassVar,
    Generic,
)

import slugid
import higlass_schema as hgs
from pydantic import BaseModel as PydanticBaseModel
from typing_extensions import Literal

from .display import renderers

TrackType = Union[hgs.EnumTrackType, Literal["heatmap"]]
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

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=PydanticBaseModel)


def _ensure_list(x: Union[None, T, List[T]]) -> List[T]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def _copy_unique(model: ModelT) -> ModelT:
    copy = model.__class__(**model.dict())
    if hasattr(copy, "uid"):
        setattr(copy, "uid", str(slugid.nice()))
    return copy


# Mixins


class _PropertiesMixin:
    def properties(self: ModelT, inplace: bool = False, **fields) -> ModelT:  # type: ignore
        model = self if inplace else _copy_unique(self)
        for k, v in fields.items():
            setattr(model, k, v)
        return model


class _OptionsMixin:
    def opts(self: "TrackT", inplace: bool = False, **options) -> "TrackT":  # type: ignore
        track = self if inplace else _copy_unique(self)
        if track.options is None:
            track.options = {}
        track.options.update(options)
        return track


class EnumTrack(hgs.EnumTrack, _OptionsMixin, _PropertiesMixin):
    ...


class HeatmapTrack(hgs.HeatmapTrack, _OptionsMixin, _PropertiesMixin):
    ...


class IndependentViewportProjectionTrack(
    hgs.IndependentViewportProjectionTrack, _OptionsMixin, _PropertiesMixin
):
    ...


class CombinedTrack(hgs.CombinedTrack, _OptionsMixin, _PropertiesMixin):
    ...



class PluginTrack(hgs.BaseTrack, _OptionsMixin, _PropertiesMixin):
    plugin_url: ClassVar[str]


Track = Union[
    EnumTrack,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    CombinedTrack,
    PluginTrack,
]

TrackT = TypeVar("TrackT", bound=Track)


class View(hgs.View[TrackT], _PropertiesMixin, Generic[TrackT]):
    def domain(
        self,
        x: Optional[hgs.Domain] = None,
        y: Optional[hgs.Domain] = None,
        inplace: bool = False,
    ):
        view = self if inplace else _copy_unique(self)
        if x is not None:
            view.initialXDomain = x
        if y is not None:
            view.initialYDomain = y
        return view

    # TODO: better name? adjust_layout, resize
    def move(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        inplace: bool = False,
    ):
        view = self if inplace else _copy_unique(self)
        if x is not None:
            view.layout.x = x
        if y is not None:
            view.layout.y = y
        if width is not None:
            view.layout.w = width
        if height is not None:
            view.layout.h = height
        return view


ViewT = TypeVar("ViewT", bound=View)


def gather_plugin_urls(views: List[ViewT]) -> List[str]:
    plugin_urls = {}
    for view in views:
        for _, track in view.tracks:
            if isinstance(track, PluginTrack):
                plugin_urls[track.type] = track.plugin_url
    return list(plugin_urls.values())


class Viewconf(hgs.Viewconf[ViewT], _PropertiesMixin, Generic[ViewT]):
    def _repr_mimebundle_(self, include=None, exclude=None):
        renderer = renderers.get()
        plugin_urls = [] if self.views is None else gather_plugin_urls(self.views)
        return renderer(self.json(), plugin_urls=plugin_urls)

    def display(self):
        """Render top-level chart using IPython.display."""
        from IPython.display import display

        display(self)

    def properties(self, inplace: bool = False, **kwargs):
        conf = self if inplace else _copy_unique(self)
        for k, v in kwargs.items():
            setattr(conf, k, v)
        return conf

    def locks(
        self,
        *locks: Union[hgs.Lock, hgs.ValueScaleLock],
        zoom: Optional[Union[List[hgs.Lock], hgs.Lock]] = None,
        location: Optional[Union[List[hgs.Lock], hgs.Lock]] = None,
        value_scale: Optional[
            Union[List[hgs.ValueScaleLock], hgs.ValueScaleLock]
        ] = None,
        inplace: bool = False,
    ):
        conf = self if inplace else _copy_unique(self)

        zoom = _ensure_list(zoom)
        location = _ensure_list(location)
        value_scale = _ensure_list(value_scale)

        shared_locks: List[hgs.Lock] = []
        for lock in locks:
            if isinstance(lock, hgs.Lock):
                shared_locks.append(lock)
            else:
                value_scale.append(lock)

        zoom.extend(shared_locks)
        location.extend(shared_locks)

        if conf.zoomLocks is None:
            conf.zoomLocks = hgs.ZoomLocks()

        for lock in zoom:
            assert isinstance(lock.uid, str)
            conf.zoomLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock:
                conf.zoomLocks.locksByViewUid[vuid] = lock.uid

        if conf.locationLocks is None:
            conf.locationLocks = hgs.LocationLocks()

        for lock in location:
            assert isinstance(lock.uid, str)
            conf.locationLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock:
                conf.locationLocks.locksByViewUid[vuid] = lock.uid

        if conf.valueScaleLocks is None:
            conf.valueScaleLocks = hgs.ValueScaleLocks()

        for lock in value_scale:
            assert isinstance(lock.uid, str)
            conf.valueScaleLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock:
                conf.valueScaleLocks.locksByViewUid[vuid] = lock.uid

        return conf


def track(
    type_: Union[hgs.EnumTrackType, Literal["heatmap"]],
    uid: Optional[str] = None,
    fromViewUid: Optional[str] = None,
    **kwargs,
) -> Track:
    if uid is None:
        uid = str(slugid.nice())

    if (
        type_
        in {
            "viewport-projection-horizontal",
            "viewport-projection-vertical",
            "viewport-projection-center",
        }
        and fromViewUid is None
    ):
        return IndependentViewportProjectionTrack(
            type=type_, uid=uid, fromViewUid=fromViewUid, **kwargs  # type: ignore
        )

    if type_ == "heatmap":
        return HeatmapTrack(type=type_, uid=uid, **kwargs)

    return EnumTrack(type=type_, uid=uid, **kwargs)


def view(
    *_tracks: Union[
        TrackT,
        Tuple[TrackT, TrackPosition],
        hgs.Tracks[TrackT],
    ],
    x: int = 0,
    y: int = 0,
    width: int = 12,
    height: int = 6,
    tracks: Optional[hgs.Tracks[TrackT]] = None,
    layout: Optional[hgs.Layout] = None,
    uid: Optional[str] = None,
    **kwargs,
) -> View[TrackT]:

    if layout is None:
        layout = hgs.Layout(x=x, y=y, w=width, h=height)
    else:
        layout = hgs.Layout(**layout.dict())

    if tracks is None:
        data = defaultdict(list)
    else:
        data = defaultdict(list, tracks.dict())

    for track in _tracks:
        if isinstance(track, hgs.Tracks):
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

    return View[TrackT](
        layout=layout,
        tracks=hgs.Tracks[TrackT](**data),
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

    copy = _copy_unique(t1)
    copy.tilesetUid = None
    copy.server = None
    copy.data = hgs.Data(
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

    return track(type_=track_type, fromViewUid=fromViewUid, **kwargs)


def viewconf(
    *_views: ViewT,
    views: Optional[List[ViewT]] = None,
    trackSourceServers: Optional[List[str]] = None,
    editable: bool = True,
    exportViewUrl: str = "http://higlass.io/api/v1/viewconfs",
    **kwargs,
) -> Viewconf[ViewT]:
    views = [] if views is None else [v.copy(deep=True) for v in views]

    for view in _views:
        views.append(view.copy(deep=True))

    if trackSourceServers is None:
        trackSourceServers = ["http://higlass.io/api/v1"]

    return Viewconf[ViewT](
        views=views,
        editable=editable,
        exportViewUrl=exportViewUrl,
        trackSourceServers=trackSourceServers,
        **kwargs,
    )


@overload
def lock(*views: View, **kwargs) -> hgs.Lock:
    ...


@overload
def lock(*pairs: Tuple[View, Track], **kwargs) -> hgs.ValueScaleLock:
    ...


def lock(*data, **kwargs):
    assert len(data) >= 1
    uid = str(slugid.nice())
    if isinstance(data[0], View):
        lck = hgs.Lock(uid=uid, **kwargs)
        for view in data:
            assert isinstance(view.uid, str)
            setattr(lck, view.uid, (1, 1, 1))
        return lck
    else:
        lck = hgs.ValueScaleLock(uid=uid, **kwargs)
        for view, track in data:
            assert isinstance(view.uid, str)
            assert isinstance(track.uid, str)
            vtuid = f"{view.uid}.{track.uid}"
            setattr(lck, vtuid, {"track": track.uid, "view": view.uid})
        return lck
