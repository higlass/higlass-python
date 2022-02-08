from collections import defaultdict
from typing import ClassVar, Generic, List, Optional, Tuple, TypeVar, Union, overload

import higlass_schema as hgs
from pydantic import BaseModel
from typing_extensions import Literal

import hg.display as display
import hg.utils as utils

## Mixins

# Can't figure out a good way to type these classes.
# We ignoring the errors in the parameter signature
# mean we can get good type information within the
# function and return types are inferred for end users.


class _PropertiesMixin:
    def properties(self: utils.ModelT, inplace: bool = False, **fields) -> utils.ModelT:  # type: ignore
        model = self if inplace else utils.copy_unique(self)
        for k, v in fields.items():
            setattr(model, k, v)
        return model


class _OptionsMixin:
    def opts(self: "TrackT", inplace: bool = False, **options) -> "TrackT":  # type: ignore

        track = self if inplace else utils.copy_unique(self)
        if track.options is None:
            track.options = {}
        track.options.update(options)
        return track


## Extend higlass-schema classes


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
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    EnumTrack,
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
        view = self if inplace else utils.copy_unique(self)
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
        view = self if inplace else utils.copy_unique(self)
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
    """Inspect tracks and extract plugin urls to inject into HTML"""
    plugin_urls = {}
    for view in views:
        for _, track in view.tracks:
            if isinstance(track, PluginTrack):
                plugin_urls[track.type] = track.plugin_url
    return list(plugin_urls.values())


class Viewconf(hgs.Viewconf[View[TrackT]], _PropertiesMixin, Generic[TrackT]):
    def _repr_mimebundle_(self, include=None, exclude=None):
        renderer = display.renderers.get()
        plugin_urls = [] if self.views is None else gather_plugin_urls(self.views)
        return renderer(self.json(), plugin_urls=plugin_urls)

    def display(self):
        """Render top-level chart using IPython.display."""
        from IPython.display import display

        display(self)

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
        conf = self if inplace else utils.copy_unique(self)

        zoom = utils.ensure_list(zoom)
        location = utils.ensure_list(location)
        value_scale = utils.ensure_list(value_scale)

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


## Top-level functions to easily create tracks,

# TODO: register plugins globally to work here?


class _TrackCreator(BaseModel):
    __root__: Track


def track(
    type_: utils.TrackType,
    uid: Optional[str] = None,
    **kwargs,
) -> Track:
    if uid is None:
        uid = utils.uid()
    data = dict(type=type_, uid=uid, **kwargs)
    return _TrackCreator.parse_obj(data).__root__


def view(
    *_tracks: Union[
        TrackT,
        Tuple[TrackT, utils.TrackPosition],
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
                position = utils.get_default_track_position(track.type)
                if position is None:
                    raise ValueError("No default track type")

            data[position].append(track)

    if uid is None:
        uid = utils.uid()

    return View[TrackT](
        layout=layout,
        tracks=hgs.Tracks[TrackT](**data),
        uid=uid,
        **kwargs,
    )


def combine(t1: Track, t2: Track, uid: Optional[str] = None, **kwargs) -> CombinedTrack:
    if uid is None:
        uid = utils.uid()

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

    copy = utils.copy_unique(t1)
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
    *_views: View[TrackT],
    views: Optional[List[View[TrackT]]] = None,
    trackSourceServers: Optional[List[str]] = None,
    editable: bool = True,
    exportViewUrl: str = "http://higlass.io/api/v1/viewconfs",
    **kwargs,
) -> Viewconf[TrackT]:
    views = [] if views is None else [v.copy(deep=True) for v in views]

    for view in _views:
        views.append(view.copy(deep=True))

    if trackSourceServers is None:
        trackSourceServers = ["http://higlass.io/api/v1"]

    return Viewconf[TrackT](
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


def lock(*data, uid: Optional[str] = None, **kwargs):
    assert len(data) >= 1
    if uid is None:
        uid = utils.uid()
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
