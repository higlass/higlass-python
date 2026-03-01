from __future__ import annotations

import abc
import functools
import pathlib
import typing
from dataclasses import dataclass

import higlass.api
from higlass._tileset_registry import TilesetInfo, TilesetRegistry
from higlass._utils import TrackType, datatype_default_track

__all__ = [
    "LocalDataTileset",
    "Tileset",
    "bed2ddb",
    "bigwig",
    "cooler",
    "hitile",
    "multivec",
    "remote",
]

DataType = typing.Literal[
    "2d-rectangle-domains",
    "bedlike",
    "chromsizes",
    "gene-annotations",
    "matrix",
    "multivec",
    "vector",
]


@dataclass
class RemoteTileset:
    uid: str
    server: str
    name: str | None = None

    def track(self, type_: TrackType, **kwargs):
        track = higlass.api.track(
            type_=type_,
            server=self.server,
            tilesetUid=self.uid,
            **kwargs,
        )
        if self.name is not None:
            track.opts(name=self.name, inplace=True)
        return track


def remote(
    uid: str, server: str = "https://higlass.io/api/v1", name: str | None = None
):
    """Create a remote tileset reference.

    Parameters
    ----------
    uid : str
        The unique identifier for the remote tileset.
    server : str, optional
        The HiGlass server URL (default is "https://higlass.io/api/v1").
    name : str, optional
        An optional name for the tileset.

    Returns
    -------
    RemoteTileset
        A RemoteTileset instance that can be used to create HiGlass tracks.
    """
    return RemoteTileset(uid, server, name)


@dataclass
class LocalDataTileset:
    """A tileset that serves data locally without a server.

    Parameters
    ----------
    tsinfo : dict
        Tileset info dict (must include ``min_pos`` and ``max_pos``).
    data : list
        Tile data for the tileset.
    """

    tsinfo: dict
    data: list

    def __post_init__(self):
        min_pos = self.tsinfo.get("min_pos", [])
        max_pos = self.tsinfo.get("max_pos", [])

        if len(min_pos) != len(max_pos):
            raise ValueError("min_pos and max_pos must have equal lengths")

        if len(min_pos) == 2:
            self._tile_key = "x.0.0.0"
        elif len(min_pos) == 1:
            self._tile_key = "x.0.0"
        else:
            raise ValueError("min_pos must be a one or two element array")

    def track(self, type_: TrackType, **kwargs) -> higlass.api.Track:
        """Create a HiGlass track with local data embedded.

        Parameters
        ----------
        type_ : TrackType
            The track type to create.
        **kwargs : dict
            Additional top-level track properties.

        Returns
        -------
        higlass.api.Track
            A track with the ``data`` section populated for local-tiles.
        """
        trk = higlass.api.track(type_=type_, **kwargs)
        trk.data = {
            "type": "local-tiles",
            "tilesetInfo": {"x": self.tsinfo},
            "tiles": {self._tile_key: self.data},
        }
        return trk


class Tileset(abc.ABC):
    """Base class for defining custom tilesets in `higlass`.

    Subclasses must implement the `tiles` and `info` methods.

    The provided `track` method is a helper which automatically registers the
    tileset with the `TilesetRegistry` and returns a HiGlass track object
    ready for visualization.

    Parameters
    ----------
    klass : type[T]
        A class implementing `TilesetProtocol`.

    Returns
    -------
    type[T]
        The input class, now with an added `track` method.

    Examples
    --------
    >>> import higlass as hg
    >>> from dataclasses import dataclass
    >>> from clodius.tiles import cooler
    >>>
    >>> @dataclass
    >>> class MyCoolerTileset(hg.Tileset):
    >>>     filepath: str
    >>>     datatype = "matrix"
    >>>
    >>>     def info(self):
    >>>         return tileset_info(self.filepath)
    >>>
    >>>     def tiles(self, tile_ids):
    >>>         return tiles(self.filepath, tile_ids)
    >>>
    >>> tileset = MyCoolerTileset("test.mcool")
    >>> hg.view(tileset.track("heatmap"))
    """

    @abc.abstractmethod
    def tiles(self, tile_ids: typing.Sequence[str], /) -> list[dict]: ...

    @abc.abstractmethod
    def info(self) -> TilesetInfo: ...

    def track(self, type_: TrackType | None = None, /, **kwargs) -> higlass.api.Track:
        """
        Create a HiGlass track for the tileset.

        Registers the tileset with the `TilesetRegistry` and returns a track
        of the given `type_`. Defaults to a type based on the tileset's `datatype`
        if not specified.

        Parameters
        ----------
        type_ : TrackType, optional
            Track type. If `None`, a default is inferred.

        Returns
        -------
        higlass.api.Track
            The configured HiGlass track.
        """
        # use default track based on datatype if available
        if type_ is None:
            datatype = getattr(self, "datatype", None)
            if datatype is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = typing.cast(TrackType, datatype_default_track[datatype])

        # add tileset registry and get an identifier
        uid = TilesetRegistry.add(self)
        track = higlass.api.track(
            type_=type_,
            server="jupyter",
            tilesetUid=uid,
            **kwargs,
        )
        name = getattr(self, "name", None)
        if name is not None:
            track.opts(name=name, inplace=True)

        return track


@dataclass
class ClodiusTileset(Tileset):
    datatype: DataType
    tiles_impl: typing.Callable[[typing.Sequence[str]], list[typing.Any]]
    info_impl: typing.Callable[[], TilesetInfo]

    def tiles(self, tile_ids: typing.Sequence[str], /) -> list[dict]:
        return self.tiles_impl(tile_ids)

    def info(self) -> TilesetInfo:
        return self.info_impl()


def create_lazy_clodius_loader(
    kind: str, datatype: DataType
) -> typing.Callable[[str | pathlib.Path], ClodiusTileset]:
    def load(filepath: str | pathlib.Path) -> ClodiusTileset:
        try:
            module = __import__(
                f"clodius.tiles.{kind}", fromlist=["tiles", "tileset_info"]
            )
        except (ImportError, AttributeError):
            raise ImportError(f"You must have `clodius` installed to use `hg.{kind}`.")

        return ClodiusTileset(
            datatype=datatype,
            tiles_impl=functools.partial(module.tiles, filepath),
            info_impl=functools.partial(module.tileset_info, filepath),
        )

    return load


def chromsizes(filepath: str) -> ClodiusTileset:
    from clodius.tiles.chromsizes import tileset_info  # ty:ignore[unresolved-import]

    return ClodiusTileset(
        datatype="chromsizes",
        tiles_impl=lambda _: {},  # chromsizes has no tiles endpoint
        info_impl=lambda: tileset_info(filepath),
    )


bed2ddb = create_lazy_clodius_loader("bed2ddb", datatype="2d-rectangle-domains")
beddb = create_lazy_clodius_loader("beddb", datatype="vector")
bigwig = create_lazy_clodius_loader("bigwig", datatype="vector")
cooler = create_lazy_clodius_loader("cooler", datatype="matrix")
hitile = create_lazy_clodius_loader("hitile", datatype="vector")
multivec = create_lazy_clodius_loader("multivec", datatype="multivec")
