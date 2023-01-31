import functools
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

import higlass_schema as hgs
from pydantic import BaseModel
from typing_extensions import Literal

import higlass.display as display
import higlass.utils as utils

__all__ = [
    "EnumTrack",
    "HeatmapTrack",
    "IndependentViewportProjectionTrack",
    "CombinedTrack",
    "PluginTrack",
    "TrackT",
    "View",
    "ViewT",
    "Viewconf",
    "concat",
    "hconcat",
    "vconcat",
    "track",
    "view",
    "combine",
    "divide",
    "lock",
]

if TYPE_CHECKING:
    from higlass.server import TilesetResource

## Mixins

# Can't figure out a good way to type these classes.
# We ignoring the errors in the parameter signature
# mean we can get good type information within the
# function and return types are inferred for end users.


class _PropertiesMixin:
    def properties(
        self: utils.ModelT, inplace: bool = False, **fields  # type: ignore
    ) -> utils.ModelT:  # type: ignore
        model = self if inplace else utils.copy_unique(self)
        for k, v in fields.items():
            setattr(model, k, v)
        return model


class _OptionsMixin:
    def opts(
        self: "TrackT",  # type: ignore
        inplace: bool = False,
        **options,
    ) -> "TrackT":  # type: ignore

        track = self if inplace else utils.copy_unique(self)
        if track.options is None:
            track.options = {}
        track.options.update(options)
        return track


class _TilesetMixin:
    def tileset(
        self: "TrackT",  # type: ignore
        tileset: "TilesetResource",
        inplace: bool = False,
    ) -> "TrackT":  # type: ignore

        track = self if inplace else utils.copy_unique(self)
        track.server = tileset.server
        track.tilesetUid = tileset.tileset.uid
        return track


## Extend higlass-schema classes


class EnumTrack(hgs.EnumTrack, _OptionsMixin, _PropertiesMixin, _TilesetMixin):
    ...


class HeatmapTrack(hgs.HeatmapTrack, _OptionsMixin, _PropertiesMixin, _TilesetMixin):
    ...


class IndependentViewportProjectionTrack(
    hgs.IndependentViewportProjectionTrack,
    _OptionsMixin,
    _PropertiesMixin,
    _TilesetMixin,
):
    ...


class CombinedTrack(hgs.CombinedTrack, _OptionsMixin, _PropertiesMixin, _TilesetMixin):
    ...


class PluginTrack(hgs.BaseTrack, _OptionsMixin, _PropertiesMixin, _TilesetMixin):
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

    def __or__(self, other: Union["View[TrackT]", "Viewconf[TrackT]"]):
        return hconcat(self, other)

    def __truediv__(self, other: Union["View[TrackT]", "Viewconf[TrackT]"]):
        return vconcat(self, other)

    def clone(self):
        return utils.copy_unique(self)

    def viewconf(self, **kwargs):
        return Viewconf[TrackT](views=[self], **kwargs)

    def display(self):
        self.viewconf().display()

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self.viewconf()._repr_mimebundle_(include, exclude)

    def widget(self, **kwargs):
        return self.viewconf().widget(**kwargs)

    def project(
        self,
        view: "View",
        on: Literal["center", "top", "bottom", "left", "right"] = "center",
        inplace: bool = False,
        **kwargs,
    ):
        new_view = self if inplace else utils.copy_unique(self)

        # projection track type from position
        if on == "center":
            track_type = "viewport-projection-center"
        elif on == "top" or on == "bottom":
            track_type = "viewport-projection-horizontal"
        elif on == "left" or on == "right":
            track_type = "viewport-projection-vertical"
        else:
            raise ValueError("Not possible")

        if getattr(new_view.tracks, on) is None:
            setattr(new_view.tracks, on, [])

        trk = track(type_=track_type, fromViewUid=view.uid, **kwargs)
        getattr(new_view.tracks, on).append(trk)

        return new_view


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

    def widget(self, **kwargs):
        from higlass_widget import HiGlassWidget

        return HiGlassWidget(self.dict())  # type: ignore

    @classmethod
    def from_url(cls, url: str):
        import urllib.request as urllib

        request = urllib.Request(url)
        with urllib.urlopen(request) as response:
            raw = response.read()

        return cls.parse_raw(raw)

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

    def __or__(
        self, other: Union[View[TrackT], "Viewconf[TrackT]"]
    ) -> "Viewconf[TrackT]":
        return hconcat(self, other)

    def __truediv__(
        self, other: Union[View[TrackT], "Viewconf[TrackT]"]
    ) -> "Viewconf[TrackT]":
        return vconcat(self, other)


def concat(
    method: Literal["horizontal", "vertical"],
    a: Union[View[TrackT], Viewconf[TrackT]],
    b: Union[View[TrackT], Viewconf[TrackT]],
):
    a = a.viewconf() if isinstance(a, View) else a
    assert a.views is not None

    b = b.viewconf() if isinstance(b, View) else b
    assert b.views is not None

    if method == "vertical":

        def mapper(view):
            return view.layout.y + view.layout.h

        field = "y"
    elif method == "horizontal":

        def mapper(view):
            return view.layout.x + view.layout.w

        field = "x"
    else:
        raise ValueError("concat method must be 'vertical' or 'horizontal'.")

    # gather views and adjust layout
    views = [v.copy(deep=True) for v in b.views]
    offset = 0 if a.views is None else max(map(mapper, a.views))
    for view in views:
        curr = getattr(view.layout, field)
        setattr(view.layout, field, curr + offset)
    a.views.extend(views)

    # merge locks
    for lockattr in ["zoomLocks", "valueScaleLocks", "locationLocks"]:
        locks = getattr(b, lockattr)
        if locks:
            if getattr(a, lockattr) is None:
                setattr(a, lockattr, locks.copy(deep=True))
            else:
                getattr(a, lockattr).locksByViewUid.update(locks.locksByViewUid)
                getattr(a, lockattr).locksDict.update(locks.locksDict)
    return a


hconcat = functools.partial(concat, "horizontal")

vconcat = functools.partial(concat, "vertical")


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
