import json
from typing import (
    Any,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, RootModel, model_validator
from typing_extensions import Annotated, Literal, TypedDict

from .utils import _GenerateJsonSchema, get_schema_of


# Override Basemodel
class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(validate_assignment=True)

    # nice repr if printing with rich
    def __rich_repr__(self):
        return iter(self)

    def json(self, exclude_none: bool = True, **kwargs):
        return super().json(exclude_none=exclude_none, **kwargs)

    def dict(self, exclude_none: bool = True, **kwargs):
        return super().dict(exclude_none=exclude_none, **kwargs)

    def model_dump(self, exclude_none: bool = True, **kwargs):
        return super().model_dump(exclude_none=exclude_none, **kwargs)

    def model_dump_json(self, exclude_none: bool = True, **kwargs):
        return super().model_dump_json(exclude_none=exclude_none, **kwargs)


##################################################
# General                                        #
##################################################

Domain = Tuple[float, float]


class OverlayOptions(BaseModel):
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
# RootModel is clunky from a python user perspective.
# We create this class to get validation for free in `root_validator`
class _LockEntryModel(RootModel[LockEntry]):
    pass


def _lock_schema_extra(schema: Dict[str, Any], _: Any) -> None:
    schema["additionalProperties"] = get_schema_of(LockEntry)


class Lock(BaseModel):
    uid: Optional[str] = None

    model_config = ConfigDict(extra="allow", json_schema_extra=_lock_schema_extra)

    def __iter__(self) -> Generator[Tuple[str, LockEntry], None, None]:
        for key, val in super().__iter__():
            if key not in self.model_fields:
                yield key, val

    # can only validate on creation for "extra" fields
    @model_validator(mode="before")
    @classmethod
    def validate_locks(cls, values: Dict[str, Any]):
        for k in values:
            if k not in cls.model_fields:
                # validate using our custom validator
                model = _LockEntryModel.model_validate(values[k])
                # get back the root type
                values[k] = model.model_dump()
        return values


class ValueScaleLockEntry(TypedDict):
    view: str
    track: str


class _ValueScaleLockEntryModel(RootModel[ValueScaleLockEntry]):
    pass


def _value_scale_lock_schema_extra(schema: Dict[str, Any], _: Any) -> None:
    schema["additionalProperties"] = get_schema_of(ValueScaleLockEntry)


class ValueScaleLock(BaseModel):
    uid: Optional[str] = None
    ignoreOffScreenValues: Optional[bool] = None

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra=_value_scale_lock_schema_extra,
    )

    def __iter__(self) -> Generator[Tuple[str, ValueScaleLockEntry], None, None]:
        for key, val in super().__iter__():
            if key not in self.model_fields:
                yield key, val

    # can only validate on creation for "extra" fields
    @model_validator(mode="before")
    @classmethod
    def validate_locks(cls, values: Dict[str, Any]):
        for k in values:
            if k not in cls.model_fields:
                # validate using our custom validator
                model = _ValueScaleLockEntryModel.model_validate(values[k])
                # read back as a regular dict
                values[k] = model.model_dump()
        return values


class AxisSpecificLock(BaseModel):
    axis: Literal["x", "y"]
    lock: str


class AxisSpecificLocks(BaseModel):
    x: Optional[AxisSpecificLock] = None
    y: Optional[AxisSpecificLock] = None


class LocationLocks(BaseModel):
    locksByViewUid: Dict[str, Union[str, AxisSpecificLocks]] = Field(
        default_factory=dict
    )
    locksDict: Dict[str, Lock] = Field(default_factory=dict)


class ZoomLocks(BaseModel):
    model_config = ConfigDict(extra="forbid")

    locksByViewUid: Dict[str, str] = Field(default_factory=dict)
    locksDict: Dict[str, Lock] = Field(default_factory=dict)


class ValueScaleLocks(BaseModel):
    model_config = ConfigDict(extra="forbid")

    locksByViewUid: Dict[str, str] = Field(default_factory=dict)
    locksDict: Dict[str, ValueScaleLock] = Field(default_factory=dict)


##################################################
# Tracks                                         #
##################################################

TrackTypeT = TypeVar("TrackTypeT", bound=str)
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


class BaseTrack(BaseModel, Generic[TrackTypeT]):
    model_config = ConfigDict(extra="allow")

    type: TrackTypeT
    uid: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    options: Optional[TrackOptions] = None


class Tileset(BaseModel):
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
    model_config = ConfigDict(extra="ignore")

    data: Optional[Data] = None
    chromInfoPath: Optional[str] = None
    fromViewUid: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None


class HeatmapTrack(BaseTrack[Literal["heatmap"]], Tileset):
    model_config = ConfigDict(extra="ignore")

    data: Optional[Data] = None
    position: Optional[str] = None
    transforms: Optional[List] = None


class IndependentViewportProjectionTrack(BaseTrack[ViewportProjectionTrackType]):
    model_config = ConfigDict(extra="ignore")

    fromViewUid: None = None
    projectionXDomain: Optional[Domain] = None
    projectionYDomain: Optional[Domain] = None
    transforms: Optional[List] = None
    x: Optional[float] = None
    y: Optional[float] = None


class CombinedTrack(BaseTrack[Literal["combined"]]):
    model_config = ConfigDict(extra="ignore")

    contents: List["Track"]
    position: Optional[str] = None


Track = Union[
    EnumTrack,
    CombinedTrack,
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    BaseTrack,
]

# CombinedTrack is recursive and needs delayed evaluation of annoations
CombinedTrack.model_rebuild()


##################################################
# View                                           #
##################################################


TrackT = TypeVar("TrackT", bound=Track)

TrackPosition = Literal["left", "right", "top", "bottom", "center", "whole", "gallery"]


class Tracks(BaseModel, Generic[TrackT]):
    """Track layout within a View."""

    model_config = ConfigDict(extra="ignore")

    left: Optional[List[TrackT]] = None
    right: Optional[List[TrackT]] = None
    top: Optional[List[TrackT]] = None
    bottom: Optional[List[TrackT]] = None
    center: Optional[List[TrackT]] = None
    whole: Optional[List[TrackT]] = None
    gallery: Optional[List[TrackT]] = None

    def __iter__(self) -> Generator[Tuple[TrackPosition, TrackT], None, None]:
        for pos, tlist in super().__iter__():
            if tlist is None:
                continue
            for track in tlist:
                yield pos, track  # type: ignore


class Layout(BaseModel):
    """Size and position of a View."""

    model_config = ConfigDict(extra="ignore")

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


class View(BaseModel, Generic[TrackT]):
    """An arrangment of Tracks to display within a given Layout."""

    model_config = ConfigDict(extra="ignore")

    layout: Layout
    tracks: Tracks[TrackT]
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

ViewT = TypeVar("ViewT", bound=View)


class Viewconf(BaseModel, Generic[ViewT]):
    """Root object describing a HiGlass visualization."""

    model_config = ConfigDict(extra="forbid")

    editable: Optional[bool] = True
    viewEditable: Optional[bool] = True
    tracksEditable: Optional[bool] = True
    zoomFixed: Optional[bool] = None
    compactLayout: Optional[bool] = None
    exportViewUrl: Optional[str] = None
    trackSourceServers: Optional[List[str]] = None
    views: Optional[Annotated[List[ViewT], Field(min_length=1)]] = None
    zoomLocks: Optional[ZoomLocks] = None
    locationLocks: Optional[LocationLocks] = None
    valueScaleLocks: Optional[ValueScaleLocks] = None
    chromInfoPath: Optional[str] = None


def schema():
    json_schema = Viewconf.model_json_schema(schema_generator=_GenerateJsonSchema)
    json_schema["$schema"] = _GenerateJsonSchema.schema_dialect
    json_schema["title"] = "HiGlass viewconf"
    return json_schema


def schema_json(**kwargs):
    return json.dumps(schema(), **kwargs)
