# generated by datamodel-codegen and modified manually ...

from __future__ import annotations

from functools import wraps
from typing import Any, Dict, List, Literal, Optional, Tuple, TypeVar, Union

import slugid
from pydantic import BaseModel as _BaseModel
from pydantic import Extra, Field, conlist, validator

from .display import renderers


# Switch pydantic defaults
class BaseModel(_BaseModel):
    class Config:
        # wether __setattr__ should perform validation
        validate_assignment = True

    # nice repr if printing with rich
    def __rich_repr__(self):
        return self.__iter__()

    # Omit fields which are None by default.
    @wraps(_BaseModel.dict)
    def dict(self, exclude_none: bool = True, **kwargs):
        return super().dict(exclude_none=exclude_none, **kwargs)

    # Omit fields which are None by default.
    @wraps(_BaseModel.json)
    def json(self, exclude_none: bool = True, **kwargs):
        return super().json(exclude_none=exclude_none, **kwargs)


class Data(BaseModel):
    url: Optional[str] = None
    server: Optional[str] = None
    filetype: Optional[str] = None
    type: Optional[str] = None
    tilesetInfo: Optional[Dict[str, Any]] = None
    children: Optional[List] = None
    tiles: Optional[Dict[str, Any]] = None


class GenomePositionSearchBox(BaseModel):
    autocompleteServer: Optional[str] = Field(
        default=None,
        examples=["//higlass.io/api/v1"],
        title="The Autocomplete Server URL",
    )
    autocompleteId: Optional[str] = Field(
        default=None, examples=["OHJakQICQD6gTD7skx4EWA"], title="The Autocomplete ID"
    )
    chromInfoServer: str = Field(
        ..., examples=["//higlass.io/api/v1"], title="The Chrominfo Server URL"
    )
    chromInfoId: str = Field(..., examples=["hg19"], title="The Chromosome Info ID")
    visible: Optional[bool] = Field(False, title="The Visible Schema")


class Layout(BaseModel):
    class Config:
        extra = Extra.forbid

    x: int = Field(..., title="The X Position")
    y: int = Field(..., title="The Y Position")
    w: int = Field(..., title="Width")
    h: int = Field(..., title="Height")
    moved: Optional[bool] = None
    static: Optional[bool] = None


class Options(BaseModel):
    extent: Optional[List] = None
    minWidth: Optional[float] = None
    fill: Optional[str] = None
    fillOpacity: Optional[float] = None
    stroke: Optional[str] = None
    strokeOpacity: Optional[float] = None
    strokeWidth: Optional[float] = None
    strokePos: Optional[Union[str, List[Any]]] = None
    outline: Optional[str] = None
    outlineOpacity: Optional[float] = None
    outlineWidth: Optional[float] = None
    outlinePos: Optional[Union[str, List[Any]]] = None


class Overlay(BaseModel):
    class Config:
        extra = Extra.forbid

    chromInfoPath: Optional[str] = None
    includes: Optional[List] = None
    options: Optional[Options] = None
    type: Optional[str] = None
    uid: Optional[str] = None


# Simplified aliases
Domain = Tuple[int, int]
Slug = str


class AxisSpecificLocks(BaseModel):
    class Config:
        extra = Extra.forbid

    axis: Literal["x", "y"]
    lock: str


EnumTrackType = Literal[
    "multivec",
    "1d-heatmap",
    "line",
    "point",
    "bar",
    "divergent-bar",
    "stacked-interval",
    "gene-annotations",
    "linear-2d-rectangle-domains",
    "chromosome-labels",
    "linear-heatmap",
    "1d-value-interval",
    "2d-annotations",
    "2d-chromosome-annotations",
    "2d-chromosome-grid",
    "2d-chromosome-labels",
    "2d-rectangle-domains",
    "2d-tiles",
    "arrowhead-domains",
    "bedlike",
    "cross-rule",
    "dummy",
    "horizontal-1d-annotations",
    "horizontal-1d-heatmap",
    "horizontal-1d-tiles",
    "horizontal-1d-value-interval",
    "horizontal-2d-rectangle-domains",
    "horizontal-bar",
    "horizontal-chromosome-grid",
    "horizontal-chromosome-labels",
    "horizontal-divergent-bar",
    "horizontal-gene-annotations",
    "horizontal-heatmap",
    "horizontal-line",
    "horizontal-multivec",
    "horizontal-point",
    "horizontal-rule",
    "horizontal-vector-heatmap",
    "image-tiles",
    "left-axis",
    "left-stacked-interval",
    "mapbox-tiles",
    "osm-2d-tile-ids",
    "osm-tiles",
    "raster-tiles",
    "simple-svg",
    "square-markers",
    "top-axis",
    "top-stacked-interval",
    "vertical-1d-annotations",
    "vertical-1d-heatmap",
    "vertical-1d-tiles",
    "vertical-1d-value-interval",
    "vertical-2d-rectangle-domains",
    "vertical-bar",
    "vertical-bedlike",
    "vertical-chromosome-grid",
    "vertical-chromosome-labels",
    "vertical-gene-annotations",
    "vertical-heatmap",
    "vertical-line",
    "vertical-multivec",
    "vertical-point",
    "vertical-rule",
    "vertical-vector-heatmap",
    "viewport-projection-center",
    "viewport-projection-horizontal",
    "viewport-projection-vertical",
]


T = TypeVar("T", bound=BaseModel)


def _copy_unique(model: T) -> T:
    copy = model.__class__(**model.dict())
    if hasattr(copy, "uid"):
        setattr(copy, "uid", str(slugid.nice()))
    return copy


class BaseTrack(BaseModel):
    class Config:
        extra = Extra.forbid

    uid: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    options: Optional[Dict[str, Any]] = None

    def opts(self, inplace: bool = False, **options):
        track = self if inplace else _copy_unique(self)
        if track.options is None:
            track.options = {}
        track.options.update(options)
        return track

    def properties(self, inplace: bool = False, **fields):
        track = self if inplace else _copy_unique(self)
        for k, v in fields.items():
            setattr(track, k, v)
        return track


class EnumTrack(BaseTrack):
    type: EnumTrackType
    server: Optional[str] = None
    tilesetUid: Optional[str] = None
    data: Optional[Data] = None
    chromInfoPath: Optional[str] = None
    fromViewUid: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None


class HeatmapTrack(BaseTrack):
    type: Literal["heatmap"]
    data: Optional[Data] = None
    options: Optional[Dict[str, Any]] = None
    position: Optional[str] = None
    server: Optional[str] = None
    tilesetUid: Optional[str] = None
    transforms: Optional[List] = None


class IndependentViewportProjectionTrack(BaseTrack):
    type: Literal[
        "viewport-projection-horizontal",
        "viewport-projection-vertical",
        "viewport-projection-center",
    ]
    fromViewUid: None = None
    projectionXDomain: Optional[Domain] = None
    projectionYDomain: Optional[Domain] = None
    options: Optional[Dict[str, Any]] = None
    transforms: Optional[List] = None
    x: Optional[float] = None
    y: Optional[float] = None


class CombinedTrack(BaseTrack):
    type: Literal["combined"]
    contents: List["Track"]
    position: Optional[str] = None


Track = Union[
    EnumTrack,
    CombinedTrack,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
]


class Lock(BaseModel):
    class Config:
        extra = Extra.allow

    uid: Optional[Slug] = None

    def __iter_uids__(self):
        for uid, val in self:
            if not uid == "uid":
                yield uid, val


class LocationLocks(BaseModel):
    class Config:
        extra = Extra.forbid

    locksByViewUid: Dict[str, Union[str, AxisSpecificLocks]] = {}
    locksDict: Dict[str, Lock] = {}


class ZoomLocks(BaseModel):
    class Config:
        extra = Extra.forbid

    locksByViewUid: Dict[str, str] = {}
    locksDict: Dict[str, Lock] = {}


class ValueScaleLock(BaseModel):
    class Config:
        extra = Extra.allow

    uid: Optional[Slug] = None
    ignoreOffScreenValues: Optional[bool] = None

    def __iter_uids__(self):
        for uid, val in self:
            if uid not in ("uid", "ignoreOffScreenValues"):
                yield uid, val


class ValueScaleLocks(BaseModel):
    class Config:
        extra = Extra.forbid

    locksByViewUid: Dict[str, str] = {}
    locksDict: Dict[str, ValueScaleLock] = {}


def _ensure_list(x: Union[None, T, List[T]]) -> List[T]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


class Viewconf(BaseModel):
    class Config:
        extra = Extra.forbid

    editable: Optional[bool] = True
    viewEditable: Optional[bool] = True
    tracksEditable: Optional[bool] = True
    zoomFixed: Optional[bool] = None
    compactLayout: Optional[bool] = None
    exportViewUrl: Optional[str] = None
    trackSourceServers: Optional[conlist(str, min_items=1)] = None
    zoomLocks: Optional[ZoomLocks] = None
    locationLocks: Optional[LocationLocks] = None
    valueScaleLocks: Optional[ValueScaleLocks] = None
    views: Optional[conlist(View, min_items=1)] = None
    chromInfoPath: Optional[str] = None

    def _repr_mimebundle_(self, include=None, exclude=None):
        renderer = renderers.get()
        return renderer(self.json())

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
        *locks: Union[Lock, ValueScaleLock],
        zoom: Optional[Union[List[Lock], Lock]] = None,
        location: Optional[Union[List[Lock], Lock]] = None,
        value_scale: Optional[Union[List[ValueScaleLock], ValueScaleLock]] = None,
        inplace: bool = False,
    ):
        conf = self if inplace else _copy_unique(self)

        zoom = _ensure_list(zoom)
        location = _ensure_list(location)
        value_scale = _ensure_list(value_scale)

        shared_locks: List[Lock] = []
        for lock in locks:
            if isinstance(lock, Lock):
                shared_locks.append(lock)
            else:
                value_scale.append(lock)

        zoom.extend(shared_locks)
        location.extend(shared_locks)

        if conf.zoomLocks is None:
            conf.zoomLocks = ZoomLocks()

        for lock in zoom:
            assert isinstance(lock.uid, str)
            conf.zoomLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock.__iter_uids__():
                conf.zoomLocks.locksByViewUid[vuid] = lock.uid

        if conf.locationLocks is None:
            conf.locationLocks = LocationLocks()

        for lock in location:
            assert isinstance(lock.uid, str)
            conf.locationLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock.__iter_uids__():
                conf.locationLocks.locksByViewUid[vuid] = lock.uid

        if conf.valueScaleLocks is None:
            conf.valueScaleLocks = ValueScaleLocks()

        for lock in value_scale:
            assert isinstance(lock.uid, str)
            conf.valueScaleLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock.__iter_uids__():
                conf.valueScaleLocks.locksByViewUid[vuid] = lock.uid

        return conf


class View(BaseModel):
    class Config:
        extra = Extra.forbid

    layout: Layout
    tracks: Tracks
    uid: Optional[str] = None
    autocompleteSource: Optional[str] = None
    chromInfoPath: Optional[str] = None
    genomePositionSearchBox: Optional[GenomePositionSearchBox] = None
    genomePositionSearchBoxVisible: Optional[bool] = None
    initialXDomain: Optional[Domain] = None
    initialYDomain: Optional[Domain] = None
    overlays: Optional[List[Overlay]] = None
    selectionView: Optional[bool] = None
    zoomFixed: Optional[bool] = None
    zoomLimits: Tuple[float, Optional[float]] = (1, None)

    def properties(self, inplace: bool = False, **kwargs):
        view = self if inplace else _copy_unique(self)
        for k, v in kwargs.items():
            setattr(view, k, v)
        return view

    def domain(
        self,
        x: Optional[Domain] = None,
        y: Optional[Domain] = None,
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


class Tracks(BaseModel):
    class Config:
        extra = Extra.forbid

    left: Optional[List[Track]] = None
    right: Optional[List[Track]] = None
    top: Optional[List[Track]] = None
    bottom: Optional[List[Track]] = None
    center: Optional[List[Track]] = None
    whole: Optional[List[Track]] = None
    gallery: Optional[List[Track]] = None

    @validator("*", pre=True)
    def ensure_list(cls, v):
        if v is not None and not isinstance(v, (tuple, list)):
            v = [v]
        return v


Viewconf.update_forward_refs()
View.update_forward_refs()
Tracks.update_forward_refs()
CombinedTrack.update_forward_refs()
