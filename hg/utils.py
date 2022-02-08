from typing import Dict, List, Optional, TypeVar, Union

import higlass_schema as hgs
import slugid
from pydantic import BaseModel
from typing_extensions import Literal

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=BaseModel)

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

_datatype_default_track = {
    "2d-rectangle-domains": "2d-rectangle-domains",
    "bedlike": "bedlike",
    "chromsizes": "horizontal-chromosome-labels",
    "gene-annotations": "horizontal-gene-annotations",
    "matrix": "heatmap",
    "vector": "horizontal-bar",
    "multivec": "horizontal-multivec",
}


def uid():
    return str(slugid.nice())


def get_default_track_position(track_type: str) -> Optional[TrackPosition]:
    return _track_default_position.get(track_type, None)


def ensure_list(x: Union[None, T, List[T]]) -> List[T]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def copy_unique(model: ModelT) -> ModelT:
    """Creates a deep copy of a pydantic BaseModel with new UID"""
    copy = model.__class__(**model.dict())
    if hasattr(copy, "uid"):
        setattr(copy, "uid", uid())
    return copy
