from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any, Dict, Generator, List, Optional, Tuple, TypedDict, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra, Field, conlist
from pydantic.class_validators import root_validator
from typing_extensions import Literal

from .utils import exclude_properties_titles, get_schema_of, simplify_enum_schema


# Override Pydantic defaults
class BaseModel(PydanticBaseModel):
    class Config:
        extra = Extra.forbid
        schema_extra = staticmethod(lambda s, _: exclude_properties_titles(s))


##################################################
# General                                        #
##################################################

Domain = Tuple[float, float]


class OverlayOptions(BaseModel):
    class Config:
        extra = Extra.ignore

    extent: Optional[List[List[int]]] = None
    minWidth: Optional[float] = None
    fill: Optional[str] = None
    fillOpacity: Optional[float] = None
    stroke: Optional[str] = None
    strokeOpacity: Optional[float] = None
    strokeWidth: Optional[float] = None
    strokePos: Optional[Union[str, List[str]]] = None
    outline: Optional[str] = None
    outlineOpacity: Optional[float] = None
    outlineWidth: Optional[float] = None
    outlinePos: Optional[Union[str, List[str]]] = None


class Overlay(BaseModel):
    type: Optional[str] = None
    uid: Optional[str] = None
    chromInfoPath: Optional[str] = None
    includes: Optional[List[str]] = None
    options: Optional[OverlayOptions] = None


##################################################
# Locks                                          #
##################################################


# Locks are tricky to describe with python's type system
# because _some_ keys are static (e.g., the lock `uid`) while
# the rest of the keys are dynamic (the view uids) and
# satisfy a different type constraint.
#
# In JSON schema, this is type can be described using an "object"
# "type" with "additionalProperties" or "patternProperties" field.
#
# ```json
# {
#   "type": "object",
#   "properties": {
#     "uid": { "type: "string" }
#   },
#   "additionalProperties": {
#     "type": "array",
#     "minLength": 3,
#     "maxLength": 3,
#     "items": [
#       { "type": "number" },
#       { "type": "number" },
#       { "type": "number" }
#     ]
#   }
# }
# ```
#
# The lock classes implement pydantic Models which:
#
# (1) Performs the appropriate validation/serde for this object
#
# (2) Exports the appropriate JSON schema using "additionalProperties"
#     field via a custom `schema_extra` extension.
#
# This could probably be implemented generally with
# pydantic.generics.Generic/typing.Generic, but we implement
# concretely for the different lock types.


LockEntry = Tuple[float, float, float]

# We'd rather have tuples in our final model, because a
# __root__ model is clunky from a python user perspective.
# We create this class to get validation for free in `root_validator`
class _LockEntryModel(BaseModel):
    __root__: LockEntry


class Lock(BaseModel):
    uid: Optional[str] = None

    class Config:
        extra = Extra.allow

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _) -> None:
            exclude_properties_titles(schema)
            schema["additionalProperties"] = get_schema_of(LockEntry)

    def __iter__(self) -> Generator[Tuple[str, LockEntry], None, None]:
        for key, val in super().__iter__():
            if key not in self.__fields__:
                yield key, val

    # can only validate on creation for "extra" fields
    @root_validator(pre=True)
    def validate_locks(cls, values: Dict[str, Any]):
        for k in values:
            if k not in cls.__fields__:
                # validate using our custom validator
                model = _LockEntryModel.parse_obj(values[k])
                # get back the root type
                values[k] = model.__root__
        return values


class ValueScaleLockEntry(TypedDict):
    view: str
    track: str


class _ValueScaleLockEntryModel(BaseModel):
    __root__: ValueScaleLockEntry


class ValueScaleLock(BaseModel):
    uid: Optional[str] = None
    ignoreOffScreenValues: Optional[bool] = None

    class Config:
        extra = Extra.allow

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _) -> None:
            exclude_properties_titles(schema)
            schema["additionalProperties"] = get_schema_of(ValueScaleLockEntry)

    def __iter__(self) -> Generator[Tuple[str, ValueScaleLockEntry], None, None]:
        for key, val in super().__iter__():
            if key not in self.__fields__:
                yield key, val

    # can only validate on creation for "extra" fields
    @root_validator(pre=True)
    def validate_locks(cls, values: Dict[str, Any]):
        for k in values:
            if k not in cls.__fields__:
                # validate using our custom validator
                model = _ValueScaleLockEntryModel.parse_obj(values[k])
                # read back as a regular dict
                values[k] = model.__root__
        return values


class AxisSpecificLock(BaseModel):
    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], _: Any) -> None:
            exclude_properties_titles(schema)
            schema["properties"]["axis"] = simplify_enum_schema(
                schema["properties"]["axis"]
            )

    axis: Literal["x", "y"]
    lock: str


class AxisSpecificLocks(BaseModel):
    x: Optional[AxisSpecificLock] = None
    y: Optional[AxisSpecificLock] = None


class LocationLocks(BaseModel):
    locksByViewUid: Dict[str, Union[str, AxisSpecificLocks]] = {}
    locksDict: Dict[str, Lock] = {}


class ZoomLocks(BaseModel):
    class Config:
        extra = Extra.forbid

    locksByViewUid: Dict[str, str] = {}
    locksDict: Dict[str, Lock] = {}


class ValueScaleLocks(BaseModel):
    class Config:
        extra = Extra.forbid

    locksByViewUid: Dict[str, str] = {}
    locksDict: Dict[str, ValueScaleLock] = {}


##################################################
# Tracks                                         #
##################################################

TrackOptions = Dict[str, Any]
TilesetInfo = Dict[str, Any]
Tile = Dict[str, Any]


class Data(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    server: Optional[str] = None
    filetype: Optional[str] = None
    children: Optional[List] = None
    tilesetInfo: Optional[TilesetInfo] = None
    tiles: Optional[Tile] = None


from typing import Generic, TypeVar

from pydantic.generics import GenericModel

TrackType = TypeVar("TrackType", bound=str)


class BaseTrack(GenericModel, Generic[TrackType]):
    class Config:
        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _: Any) -> None:
            exclude_properties_titles(schema)
            schema["properties"]["type"] = simplify_enum_schema(
                schema["properties"]["type"]
            )

    type: TrackType
    uid: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    options: Optional[TrackOptions] = None


class Tileset(BaseModel):
    class Config:
        extra = Extra.forbid

    tilesetUid: Optional[str] = None
    server: Optional[str] = None


ViewportProjectionTrackType = Literal[
    "viewport-projection-center",
    "viewport-projection-vertical",
    "viewport-projection-horizontal",
]

EnumTrackType = Union[
    ViewportProjectionTrackType,
    Literal[
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
    ],
]


class EnumTrack(BaseTrack[EnumTrackType], Tileset):
    data: Optional[Data] = None
    chromInfoPath: Optional[str] = None
    fromViewUid: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None


class HeatmapTrack(BaseTrack[Literal["heatmap"]], Tileset):
    data: Optional[Data] = None
    position: Optional[str] = None
    transforms: Optional[List] = None


class IndependentViewportProjectionTrack(BaseTrack[ViewportProjectionTrackType]):
    fromViewUid: None = None
    projectionXDomain: Optional[Domain] = None
    projectionYDomain: Optional[Domain] = None
    transforms: Optional[List] = None
    x: Optional[float] = None
    y: Optional[float] = None


class CombinedTrack(BaseTrack[Literal["combined"]]):
    contents: List[Track]
    position: Optional[str] = None


Track = Union[
    EnumTrack,
    CombinedTrack,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
]

# CombinedTrack is recursive and needs delayed evaluation of annoations
CombinedTrack.update_forward_refs()


##################################################
# View                                           #
##################################################


class Tracks(BaseModel):
    """Track layout within a View."""

    class Config:
        extra = Extra.forbid

    left: Optional[List[Track]] = None
    right: Optional[List[Track]] = None
    top: Optional[List[Track]] = None
    bottom: Optional[List[Track]] = None
    center: Optional[List[Track]] = None
    whole: Optional[List[Track]] = None
    gallery: Optional[List[Track]] = None


class Layout(BaseModel):
    """Size and position of a View."""

    class Config:
        extra = Extra.forbid

    x: int = Field(default=0, description="The X Position")
    y: int = Field(default=0, description="The Y Position")
    w: int = Field(default=12, description="Width")
    h: int = Field(default=12, description="Height")
    moved: Optional[bool] = None
    static: Optional[bool] = None


class GenomePositionSearchBox(BaseModel):
    """Locations to search within a View."""

    autocompleteServer: Optional[str] = Field(
        default=None,
        examples=["//higlass.io/api/v1"],
        description="The Autocomplete Server URL",
    )
    autocompleteId: Optional[str] = Field(
        default=None,
        examples=["OHJakQICQD6gTD7skx4EWA"],
        description="The Autocomplete ID",
    )
    chromInfoServer: Optional[str] = Field(
        default=None,
        examples=["//higlass.io/api/v1"],
        description="The Chrominfo Server URL",
    )
    chromInfoId: Optional[str] = Field(
        default=None,
        examples=["hg19"],
        description="The Chromosome Info ID",
    )
    visible: Optional[bool] = Field(
        default=None,
        description="The Visible Schema",
    )


class View(BaseModel):
    """An arrangment of Tracks to display within a given Layout."""

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


##################################################
# Viewconf                                       #
##################################################


class Viewconf(BaseModel):
    """Root object describing a HiGlass visualization."""

    class Config:
        extra = Extra.forbid
        title = "HiGlass viewconf"

    editable: Optional[bool] = True
    viewEditable: Optional[bool] = True
    tracksEditable: Optional[bool] = True
    zoomFixed: Optional[bool] = None
    compactLayout: Optional[bool] = None
    exportViewUrl: Optional[str] = None
    trackSourceServers: Optional[conlist(str, min_items=1)] = None
    views: Optional[conlist(View, min_items=1)] = None
    zoomLocks: Optional[ZoomLocks] = None
    locationLocks: Optional[LocationLocks] = None
    valueScaleLocks: Optional[ValueScaleLocks] = None
    chromInfoPath: Optional[str] = None


def schema():
    root = Viewconf.schema()

    # remove titles in defintions
    for d in root["definitions"].values():
        d.pop("title", None)

    # nice ordering
    ordered_root = OrderedDict(
        [
            ("$schema", "http://json-schema.org/draft-07/schema#"),
            ("$id", "https://higlass.io/#viewconf"),
            *root.items(),
        ]
    )

    return dict(ordered_root)


def schema_json(**kwargs):
    return json.dumps(schema(), **kwargs)
