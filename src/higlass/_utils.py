from __future__ import annotations

import uuid
from typing import Literal, TypeVar, Union

import higlass_schema as hgs
from pydantic import BaseModel

TrackType = Union[hgs.EnumTrackType, Literal["heatmap"]]
TrackPosition = Literal["center", "top", "left", "bottom", "center", "whole", "gallery"]

track_default_position: dict[str, TrackPosition] = {
    "1d-heatmap": "top",
    "2d-rectangle-domains": "center",
    "bar": "top",
    "bedlike": "top",
    "chromosome-labels": "top",
    "gene-annotations": "top",
    "heatmap": "center",
    "horizontal-1d-heatmap": "top",
    "horizontal-bar": "top",
    "horizontal-chromosome-labels": "top",
    "horizontal-gene-annotations": "top",
    "horizontal-heatmap": "top",
    "horizontal-line": "top",
    "horizontal-multivec": "top",
    "left-axis": "left",
    "line": "top",
    "osm-tiles": "center",
    "top-axis": "top",
    "viewport-projection-center": "center",
    "viewport-projection-horizontal": "top",
    "vertical-chromosome-labels": "left",
    "vertical-gene-annotations": "left",
}

datatype_default_track = {
    "2d-rectangle-domains": "2d-rectangle-domains",
    "bedlike": "bedlike",
    "chromsizes": "horizontal-chromosome-labels",
    "gene-annotations": "horizontal-gene-annotations",
    "matrix": "heatmap",
    "multivec": "horizontal-multivec",
    "vector": "horizontal-bar",
}


def uid() -> str:
    return str(uuid.uuid4()).split("-")[0]


T = TypeVar("T")


def ensure_list(x: T | list[T] | None) -> list[T]:
    """Ensures that x is a list.

    Parameters
    ----------
    x : T | list[T] | None
        The object to be converted to a list.

    Returns
    -------
    list[T]
        The object as a list.
    """
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


ModelT = TypeVar("ModelT", bound=BaseModel)


def copy_unique(model: ModelT) -> ModelT:
    """Creates a deep copy of a pydantic BaseModel with new UID."""
    copy = model.model_copy(deep=True)
    if hasattr(copy, "uid"):
        setattr(copy, "uid", uid())
    return copy
